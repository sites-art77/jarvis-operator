from __future__ import annotations

import base64
import json
import re
from typing import Any

import httpx

from jarvis.config import NVIDIA_VISION_FALLBACKS, Settings

VISION_PROMPT = (
    "Descreva a tela do computador para um operador. "
    "Cite a janela em foco, textos visíveis, botões, ícones e campos. "
    "Para cada alvo clicável, estime x,y em percentual (0-100) da tela. "
    "Não invente o que não estiver visível."
)


def jpeg_data_url(jpeg: bytes) -> str:
    b64 = base64.b64encode(jpeg).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"


def parse_args(raw: str) -> dict[str, Any]:
    if not raw:
        return {}
    if isinstance(raw, dict):
        return raw
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def strip_reasoning(text: str) -> str:
    return re.sub(r"<think>[\s\S]*?</think>", "", text or "", flags=re.I).replace("/no_think", "").strip()


def parse_embedded_tools(content: str) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    tagged = re.compile(r"<tool_call>\s*([\s\S]*?)\s*</tool_call>", re.I)
    for i, match in enumerate(tagged.finditer(content or "")):
        try:
            json_blob = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        name = json_blob.get("name")
        if not name:
            continue
        args = json_blob.get("arguments") or json_blob.get("parameters") or {}
        calls.append(
            {
                "id": f"embed-{i}",
                "type": "function",
                "function": {
                    "name": name,
                    "arguments": args if isinstance(args, str) else json.dumps(args, ensure_ascii=False),
                },
            }
        )
    return calls


class Brain:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client = httpx.Client(timeout=90.0)

    def chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        payload_messages = list(messages)
        if self.settings.provider == "nvidia" and payload_messages:
            first = payload_messages[0]
            if first.get("role") == "system" and "nemotron" in self.settings.model.lower():
                content = first.get("content") or ""
                if "/no_think" not in content:
                    payload_messages[0] = {**first, "content": content + "\n/no_think"}
        body: dict[str, Any] = {
            "model": self.settings.model,
            "messages": payload_messages,
            "temperature": 0.2,
            "max_tokens": 1400,
        }
        if tools:
            body["tools"] = tools
            body["tool_choice"] = "auto"
        r = self._client.post(
            f"{self.settings.api_base}/chat/completions",
            headers=self.settings.headers,
            json=body,
        )
        if r.status_code >= 400:
            raise RuntimeError(f"{self.settings.provider} chat {r.status_code}: {r.text[:500]}")
        data = r.json()
        message = data["choices"][0]["message"]
        content = strip_reasoning(message.get("content") or "")
        message["content"] = content or None
        if not message.get("tool_calls"):
            embedded = parse_embedded_tools(content)
            if embedded:
                message["tool_calls"] = embedded
                message["content"] = None
        return message

    def see(self, jpeg: bytes, caption: str) -> str:
        models: list[str] = []
        for model in (self.settings.vision_model, *NVIDIA_VISION_FALLBACKS):
            if model and model not in models:
                models.append(model)
        last_status = 0
        for model in models:
            body = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": jpeg_data_url(jpeg)}},
                            {"type": "text", "text": f"{caption}\n{VISION_PROMPT}"},
                        ],
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 700,
            }
            r = self._client.post(
                f"{self.settings.api_base}/chat/completions",
                headers=self.settings.headers,
                json=body,
            )
            if r.status_code >= 400:
                last_status = r.status_code
                continue
            data = r.json()
            text = strip_reasoning((data.get("choices") or [{}])[0].get("message", {}).get("content") or "")
            if text:
                return f"{caption}\nvisão ({model}):\n{text[:5500]}"
        if self.settings.xai_key:
            r = self._client.post(
                "https://api.x.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.settings.xai_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "grok-4.5",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": f"{caption}\n{VISION_PROMPT}"},
                                {"type": "image_url", "image_url": {"url": jpeg_data_url(jpeg), "detail": "high"}},
                            ],
                        }
                    ],
                    "temperature": 0.1,
                    "max_tokens": 700,
                },
            )
            if r.status_code < 400:
                data = r.json()
                text = (data.get("choices") or [{}])[0].get("message", {}).get("content") or ""
                if text.strip():
                    return f"{caption}\nvisão (grok):\n{text.strip()[:5500]}"
        return f"(visão indisponível {last_status}) {caption}"

    def tts(self, text: str) -> bytes:
        key = self.settings.xai_key
        if not key:
            raise RuntimeError("voz exige XAI_API_KEY no .env, além da NVIDIA")
        r = self._client.post(
            "https://api.x.ai/v1/tts",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={
                "text": text[:500],
                "voice_id": self.settings.voice,
                "language": "pt" if self.settings.lang.startswith("pt") else "en",
            },
        )
        if r.status_code >= 400:
            raise RuntimeError(f"xAI tts {r.status_code}: {r.text[:300]}")
        return r.content

    def transcribe(self, wav_bytes: bytes) -> str:
        key = self.settings.xai_key
        if not key:
            raise RuntimeError("transcrição exige XAI_API_KEY no .env")
        r = self._client.post(
            "https://api.x.ai/v1/stt",
            headers={"Authorization": f"Bearer {key}"},
            files={"file": ("speech.wav", wav_bytes, "audio/wav")},
            data={"model": "grok-voice-transcribe-1.0"},
        )
        if r.status_code >= 400:
            raise RuntimeError(f"xAI stt {r.status_code}: {r.text[:300]}")
        payload = r.json()
        if isinstance(payload, dict):
            return str(payload.get("text") or payload.get("transcript") or "").strip()
        return str(payload).strip()


XAI = Brain

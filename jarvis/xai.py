from __future__ import annotations

import base64
import json
from typing import Any

import httpx

from jarvis.config import Settings


class XAI:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client = httpx.Client(timeout=90.0)

    def chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {
            "model": self.settings.model,
            "messages": messages,
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
            raise RuntimeError(f"xAI chat {r.status_code}: {r.text[:500]}")
        data = r.json()
        return data["choices"][0]["message"]

    def tts(self, text: str) -> bytes:
        r = self._client.post(
            f"{self.settings.api_base}/tts",
            headers=self.settings.headers,
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
        files = {"file": ("speech.wav", wav_bytes, "audio/wav")}
        data = {"model": "grok-voice-transcribe-1.0"}
        headers = {"Authorization": f"Bearer {self.settings.api_key}"}
        r = self._client.post(
            f"{self.settings.api_base}/stt",
            headers=headers,
            files=files,
            data=data,
        )
        if r.status_code >= 400:
            raise RuntimeError(f"xAI stt {r.status_code}: {r.text[:300]}")
        payload = r.json()
        if isinstance(payload, dict):
            return str(payload.get("text") or payload.get("transcript") or "").strip()
        return str(payload).strip()


def jpeg_data_url(jpeg: bytes) -> str:
    b64 = base64.b64encode(jpeg).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"


def parse_args(raw: str) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}

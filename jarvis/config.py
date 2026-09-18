from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

NVIDIA_BASE = "https://integrate.api.nvidia.com/v1"
XAI_BASE = "https://api.x.ai/v1"
NVIDIA_MODEL = "meta/llama-3.3-70b-instruct"
NVIDIA_VISION = "nvidia/llama-3.1-nemotron-nano-vl-8b-v1"
XAI_MODEL = "grok-4.5"


@dataclass(frozen=True)
class Settings:
    provider: str
    api_key: str
    api_base: str
    model: str
    vision_model: str
    lang: str
    voice: str
    max_steps: int
    xai_key: str

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    @property
    def can_speak(self) -> bool:
        return bool(self.xai_key)


def _pick_provider() -> str:
    forced = (os.environ.get("JARVIS_PROVIDER") or "auto").strip().lower()
    nvidia = (os.environ.get("NVIDIA_API_KEY") or "").strip()
    xai = (os.environ.get("XAI_API_KEY") or "").strip()
    if forced in {"nvidia", "xai"}:
        return forced
    if nvidia:
        return "nvidia"
    if xai:
        return "xai"
    return ""


def load_settings() -> Settings:
    provider = _pick_provider()
    nvidia = (os.environ.get("NVIDIA_API_KEY") or "").strip()
    xai = (os.environ.get("XAI_API_KEY") or "").strip()
    if provider == "nvidia":
        if not nvidia:
            raise SystemExit(
                "NVIDIA_API_KEY ausente. Crie a chave em https://build.nvidia.com "
                "e coloque no .env local — nunca no git."
            )
        key, base = nvidia, NVIDIA_BASE
        model = (os.environ.get("JARVIS_MODEL") or NVIDIA_MODEL).strip() or NVIDIA_MODEL
        vision = (os.environ.get("JARVIS_VISION_MODEL") or NVIDIA_VISION).strip() or NVIDIA_VISION
    elif provider == "xai":
        if not xai:
            raise SystemExit(
                "XAI_API_KEY ausente. Copie .env.example para .env e coloque a chave "
                f"({Path.cwd() / '.env'})."
            )
        key, base = xai, XAI_BASE
        model = (os.environ.get("JARVIS_MODEL") or XAI_MODEL).strip() or XAI_MODEL
        vision = model
    else:
        raise SystemExit(
            "Nenhuma chave. No .env local coloque NVIDIA_API_KEY (build.nvidia.com) "
            "e/ou XAI_API_KEY (console.x.ai). Nunca commite o .env."
        )
    return Settings(
        provider=provider,
        api_key=key,
        api_base=os.environ.get("JARVIS_API_BASE", base).strip() or base,
        model=model,
        vision_model=vision,
        lang=os.environ.get("JARVIS_LANG", "pt-BR").strip() or "pt-BR",
        voice=os.environ.get("JARVIS_VOICE", "altair").strip() or "altair",
        max_steps=max(1, int(os.environ.get("JARVIS_MAX_STEPS", "20"))),
        xai_key=xai,
    )

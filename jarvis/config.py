from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    api_key: str
    model: str
    lang: str
    voice: str
    max_steps: int
    api_base: str = "https://api.x.ai/v1"

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }


def load_settings() -> Settings:
    key = (os.environ.get("XAI_API_KEY") or "").strip()
    if not key:
        env_path = Path.cwd() / ".env"
        raise SystemExit(
            "XAI_API_KEY ausente. Copie .env.example para .env e coloque a chave "
            f"do console.x.ai ({env_path})."
        )
    return Settings(
        api_key=key,
        model=os.environ.get("JARVIS_MODEL", "grok-4.5").strip() or "grok-4.5",
        lang=os.environ.get("JARVIS_LANG", "pt-BR").strip() or "pt-BR",
        voice=os.environ.get("JARVIS_VOICE", "altair").strip() or "altair",
        max_steps=max(1, int(os.environ.get("JARVIS_MAX_STEPS", "20"))),
    )

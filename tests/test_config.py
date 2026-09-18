import pytest

from jarvis.config import load_settings


def test_nvidia_key_selects_nvidia_provider(monkeypatch):
    monkeypatch.setenv("NVIDIA_API_KEY", "nvapi-test")
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    monkeypatch.delenv("JARVIS_PROVIDER", raising=False)
    monkeypatch.delenv("JARVIS_MODEL", raising=False)
    s = load_settings()
    assert s.provider == "nvidia"
    assert "nvidia.com" in s.api_base
    assert s.model.startswith("meta/") or s.model.startswith("nvidia/")


def test_xai_when_only_xai(monkeypatch):
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    monkeypatch.delenv("JARVIS_PROVIDER", raising=False)
    monkeypatch.delenv("JARVIS_MODEL", raising=False)
    s = load_settings()
    assert s.provider == "xai"
    assert s.model == "grok-4.5"


def test_missing_keys_exit(monkeypatch):
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    monkeypatch.delenv("JARVIS_PROVIDER", raising=False)
    with pytest.raises(SystemExit):
        load_settings()

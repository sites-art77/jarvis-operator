from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

import httpx

_BLOCKED_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "::1", "metadata.google.internal"}


def assert_public_http_url(url: str) -> str:
    raw = (url or "").strip()
    if not raw:
        raise ValueError("URL vazia")
    parsed = urlparse(raw)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("só http(s) público")
    host = (parsed.hostname or "").lower().rstrip(".")
    if not host or host in _BLOCKED_HOSTS or host.endswith(".local"):
        raise ValueError(f"host bloqueado: {host or '?'}")
    try:
        ip = ipaddress.ip_address(host)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            raise ValueError(f"IP interno bloqueado: {host}")
    except ValueError as exc:
        if "bloqueado" in str(exc) or "interno" in str(exc):
            raise
    else:
        return raw
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        raise ValueError(f"DNS falhou: {host}") from exc
    for info in infos:
        addr = info[4][0]
        ip = ipaddress.ip_address(addr)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            raise ValueError(f"resolve para IP interno: {addr}")
    return raw


def fetch_text(url: str, max_chars: int = 12_000) -> str:
    safe = assert_public_http_url(url)
    with httpx.Client(timeout=12.0, follow_redirects=True) as client:
        r = client.get(
            safe,
            headers={"User-Agent": "JARVIS-Operator/1.0"},
        )
    if r.status_code >= 400:
        return f"HTTP {r.status_code} em {safe}"
    text = r.text
    if "<" in text[:200].lower():
        import re

        text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", text)
        text = re.sub(r"(?is)<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
    text = text.strip()
    if len(text) > max_chars:
        text = text[:max_chars] + " …[cortado]"
    return f"{safe}\n{text or '(página vazia)'}"

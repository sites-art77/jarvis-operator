from __future__ import annotations

import re
from dataclasses import dataclass

CRITICAL = re.compile(
    r"""
    (
        rm\s+-rf\s+[/~]
        | mkfs
        | \bdd\b.*\bof=/dev/
        | format\s+[a-z]:
        | del\s+/s\s+/q\s+[a-z]:
        | shutdown
        | reboot
        | halt
        | poweroff
        | :\(\)\s*\{\s*:\|:
        | fork\s*bomb
        | cipher\s+/w
        | diskpart
        | reg\s+delete
        | Remove-Item\s+.*-Recurse
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)

DESTRUCTIVE = re.compile(
    r"""
    (
        rm\s+-r
        | rm\s+-rf
        | shutil\.rmtree
        | unlink
        | os\.remove
        | drop\s+table
        | drop\s+database
        | git\s+push\s+(-f|--force)
        | git\s+reset\s+--hard
        | killall
        | pkill
        | taskkill
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)


@dataclass(frozen=True)
class SafetyDecision:
    allowed: bool
    needs_confirm: bool
    reason: str


def inspect_command(command: str) -> SafetyDecision:
    text = command.strip()
    if not text:
        return SafetyDecision(False, False, "comando vazio")
    if CRITICAL.search(text):
        return SafetyDecision(
            False,
            True,
            "comando crítico bloqueado (apagar disco, desligar, fork bomb, etc.)",
        )
    if DESTRUCTIVE.search(text):
        return SafetyDecision(
            True,
            True,
            "comando destrutivo — pede confirmação no terminal",
        )
    return SafetyDecision(True, False, "ok")


def inspect_path_write(path: str) -> SafetyDecision:
    lowered = path.replace("\\", "/").lower()
    forbidden = (
        "/etc/passwd",
        "/etc/shadow",
        "/boot/",
        "c:/windows/",
        "c:\\windows\\",
        "/system32/",
    )
    if any(p in lowered for p in forbidden):
        return SafetyDecision(False, False, f"escrita recusada em caminho do sistema: {path}")
    return SafetyDecision(True, False, "ok")


def confirm(prompt: str) -> bool:
    try:
        answer = input(f"{prompt} [s/N] ").strip().lower()
    except EOFError:
        return False
    return answer in {"s", "sim", "y", "yes"}

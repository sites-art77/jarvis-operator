from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str], timeout: int = 12) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        return f"comando indisponível: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return "timeout"
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    return out or f"exit {r.returncode}"


def _safe_needle(text: str) -> str:
    return "".join(ch for ch in (text or "") if ch not in "'\";`$&|<>")[:80]


def clipboard_get() -> str:
    try:
        import pyperclip
    except ImportError:
        return "pyperclip ausente"
    try:
        text = pyperclip.paste() or ""
    except Exception as exc:
        return f"clipboard indisponível: {exc}"
    return text[:4000] or "(área de transferência vazia)"


def clipboard_set(text: str) -> str:
    try:
        import pyperclip
    except ImportError:
        return "pyperclip ausente"
    try:
        pyperclip.copy(text)
    except Exception as exc:
        return f"clipboard indisponível: {exc}"
    return f"copiou {len(text)} caracteres"


def system_info() -> str:
    total, used, free = shutil.disk_usage(Path.home())
    lines = [
        f"so: {platform.system()} {platform.release()} ({platform.machine()})",
        f"python: {platform.python_version()}",
        f"host: {platform.node()}",
        f"cpus: {os.cpu_count() or '?'}",
        f"disco home: {free // (1024**3)} GB livres / {total // (1024**3)} GB",
        f"usuario: {os.environ.get('USERNAME') or os.environ.get('USER') or '?'}",
    ]
    return "\n".join(lines)


def notify(title: str, message: str) -> str:
    title = (title or "J.A.R.V.I.S.").strip()[:80]
    message = (message or "").strip()[:240]
    if sys.platform == "darwin":
        script = f"display notification {json.dumps(message)} with title {json.dumps(title)}"
        out = _run(["osascript", "-e", script])
        return out if out.startswith("comando") else f"notificou: {title}"
    if os.name == "nt":
        t = json.dumps(title)
        m = json.dumps(message)
        ps = (
            "Add-Type -AssemblyName System.Windows.Forms; "
            "Add-Type -AssemblyName System.Drawing; "
            "$n = New-Object System.Windows.Forms.NotifyIcon; "
            "$n.Icon = [System.Drawing.SystemIcons]::Information; "
            "$n.Visible = $true; "
            f"$n.BalloonTipTitle = {t}; "
            f"$n.BalloonTipText = {m}; "
            "$n.ShowBalloonTip(5000); "
            "Start-Sleep -Seconds 6; "
            "$n.Dispose()"
        )
        subprocess.Popen(
            ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return f"notificação Windows: {title}"
    out = _run(["notify-send", title, message])
    return out if out.startswith("comando") else f"notificou: {title}"


def window_list() -> str:
    if sys.platform == "darwin":
        script = 'tell application "System Events" to get name of every process whose background only is false'
        return _run(["osascript", "-e", script])
    if os.name == "nt":
        ps = (
            "Get-Process | Where-Object { $_.MainWindowTitle } | "
            "ForEach-Object { $_.MainWindowTitle }"
        )
        return _run(["powershell", "-NoProfile", "-Command", ps])
    if shutil.which("wmctrl"):
        return _run(["wmctrl", "-l"])
    return "wmctrl ausente — instale para listar janelas no Linux"


def window_focus(title: str) -> str:
    needle = _safe_needle(title)
    if not needle:
        return "título vazio"
    if sys.platform == "darwin":
        script = (
            'tell application "System Events" to set frontmost of '
            f"first process whose name contains {json.dumps(needle)} to true"
        )
        return _run(["osascript", "-e", script]) or f"foco: {needle}"
    if os.name == "nt":
        ps = (
            f"$p = Get-Process | Where-Object {{ $_.MainWindowTitle -like '*{needle}*' }} | "
            "Select-Object -First 1; "
            "if ($p) { (New-Object -ComObject WScript.Shell).AppActivate($p.Id); "
            f"'foco: {needle}' }} else {{ 'janela não encontrada' }}"
        )
        return _run(["powershell", "-NoProfile", "-Command", ps])
    if shutil.which("wmctrl"):
        return _run(["wmctrl", "-a", needle]) or f"foco: {needle}"
    return "sem gerenciador de janelas disponível"

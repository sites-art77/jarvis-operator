from __future__ import annotations

import os
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

from jarvis.safety import inspect_command, inspect_path_write, confirm

WIN_ALIASES = {
    "bloco de notas": "notepad.exe",
    "bloco-de-notas": "notepad.exe",
    "notepad": "notepad.exe",
    "anotacoes": "notepad.exe",
    "calculadora": "calc.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "explorer": "explorer.exe",
    "arquivos": "explorer.exe",
    "pasta": "explorer.exe",
    "paint": "mspaint.exe",
    "cmd": "cmd.exe",
    "prompt": "cmd.exe",
    "powershell": "powershell.exe",
    "terminal": "wt.exe",
    "edge": "msedge",
    "chrome": "chrome",
    "google chrome": "chrome",
    "firefox": "firefox",
    "code": "code",
    "vscode": "code",
    "visual studio code": "code",
    "spotify": "spotify",
    "discord": "discord",
    "whatsapp": "whatsapp",
    "word": "winword",
    "excel": "excel",
    "navegador": "msedge",
}


def open_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    webbrowser.open(url, new=2)
    return f"navegador aberto em {url}"


def open_path(path: str) -> str:
    target = Path(path).expanduser()
    if not target.exists():
        return f"caminho inexistente: {target}"
    if sys.platform == "darwin":
        subprocess.Popen(["open", str(target)])
    elif os.name == "nt":
        os.startfile(str(target))  # type: ignore[attr-defined]
    else:
        subprocess.Popen(["xdg-open", str(target)])
    return f"aberto: {target}"


def open_app(name: str) -> str:
    app = name.strip()
    if not app:
        return "nome de aplicativo vazio"
    if sys.platform == "darwin":
        r = subprocess.run(["open", "-a", app], capture_output=True, text=True)
        if r.returncode != 0:
            return r.stderr.strip() or f"falhou ao abrir {app}"
        return f"aplicativo {app} aberto"
    if os.name == "nt":
        resolved = WIN_ALIASES.get(app.lower(), app)
        subprocess.Popen(["cmd", "/c", "start", "", resolved], shell=False)
        return f"aplicativo {resolved} solicitado"
    bin_path = shutil.which(app)
    if bin_path:
        subprocess.Popen([bin_path])
        return f"executou {bin_path}"
    subprocess.Popen(["gtk-launch", app], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return f"gtk-launch {app}"


def list_dir(path: str, limit: int = 80) -> str:
    target = Path(path).expanduser()
    if not target.exists():
        return f"inexistente: {target}"
    if not target.is_dir():
        return f"não é pasta: {target}"
    entries = []
    for i, child in enumerate(sorted(target.iterdir())):
        if i >= limit:
            entries.append("…")
            break
        mark = "/" if child.is_dir() else ""
        entries.append(child.name + mark)
    return f"{target}:\n" + "\n".join(entries)


def read_file(path: str, max_bytes: int = 40_000) -> str:
    target = Path(path).expanduser()
    if not target.is_file():
        return f"arquivo inexistente: {target}"
    data = target.read_bytes()[:max_bytes]
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1", errors="replace")


def write_file(path: str, content: str) -> str:
    target = Path(path).expanduser()
    decision = inspect_path_write(str(target))
    if not decision.allowed:
        return decision.reason
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return f"escrito {target} ({len(content)} chars)"


def run_command(command: str, timeout: int = 30) -> str:
    decision = inspect_command(command)
    if not decision.allowed:
        return f"bloqueado: {decision.reason}"
    if decision.needs_confirm and not confirm(f"Executar comando destrutivo?\n  {command}"):
        return "comando cancelado pelo operador"
    try:
        r = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return f"timeout de {timeout}s"
    out = (r.stdout or "") + (r.stderr or "")
    out = out.strip()
    if len(out) > 8000:
        out = out[:8000] + "\n…[cortado]"
    return f"exit {r.returncode}\n{out}" if out else f"exit {r.returncode}"

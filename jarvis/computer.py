from __future__ import annotations

import io
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import mss
import pyautogui
from PIL import Image

from jarvis.safety import inspect_path_write

if os.name == "nt":
    try:
        import ctypes

        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.04


@dataclass(frozen=True)
class Screen:
    width: int
    height: int


def screen() -> Screen:
    size = pyautogui.size()
    return Screen(width=int(size.width), height=int(size.height))


def _abs(nx: float, ny: float) -> tuple[int, int]:
    """nx, ny are 0–100 percent of the primary screen."""
    s = screen()
    x = int(max(0, min(100, nx)) / 100 * (s.width - 1))
    y = int(max(0, min(100, ny)) / 100 * (s.height - 1))
    return x, y


def position() -> tuple[int, int]:
    p = pyautogui.position()
    return int(p.x), int(p.y)


def move(nx: float, ny: float, duration: float = 0.25) -> str:
    x, y = _abs(nx, ny)
    pyautogui.moveTo(x, y, duration=max(0.05, duration))
    return f"cursor em {x},{y} (tela {screen().width}x{screen().height})"


def click(nx: float | None = None, ny: float | None = None, button: str = "left", clicks: int = 1) -> str:
    if nx is not None and ny is not None:
        move(nx, ny, duration=0.18)
        time.sleep(0.05)
    btn = button if button in {"left", "right", "middle"} else "left"
    pyautogui.click(button=btn, clicks=max(1, min(clicks, 3)))
    x, y = position()
    return f"clique {btn} x{clicks} em {x},{y}"


def drag(nx: float, ny: float, duration: float = 0.35) -> str:
    x, y = _abs(nx, ny)
    pyautogui.dragTo(x, y, duration=max(0.1, duration), button="left")
    return f"arrastou até {x},{y}"


def scroll(amount: int) -> str:
    pyautogui.scroll(int(amount))
    return f"scroll {amount}"


def type_text(text: str, interval: float = 0.02) -> str:
    pyautogui.write(text, interval=max(0.0, interval))
    return f"digitou {len(text)} caracteres"


def hotkey(*keys: str) -> str:
    cleaned = [k.strip().lower() for k in keys if k and k.strip()]
    if not cleaned:
        return "nenhuma tecla"
    mapped = []
    for key in cleaned:
        if key in {"cmd", "command", "super"} and os.name == "nt":
            mapped.append("win")
        elif key in {"cmd", "command", "win"} and sys.platform == "darwin":
            mapped.append("command")
        else:
            mapped.append(key)
    pyautogui.hotkey(*mapped)
    return "teclas: " + "+".join(mapped)


def press(key: str) -> str:
    pyautogui.press(key)
    return f"tecla {key}"


def volume(action: str) -> str:
    key = {"up": "volumeup", "down": "volumedown", "mute": "volumemute"}.get((action or "").lower())
    if not key:
        return "action: up|down|mute"
    pyautogui.press(key)
    return f"volume {action}"


def media(action: str) -> str:
    key = {
        "play_pause": "playpause",
        "next": "nexttrack",
        "prev": "prevtrack",
        "stop": "stop",
    }.get((action or "").lower())
    if not key:
        return "action: play_pause|next|prev|stop"
    pyautogui.press(key)
    return f"mídia {action}"


def screenshot_jpeg(max_side: int = 1280, quality: int = 72) -> tuple[bytes, Screen]:
    with mss.mss() as sct:
        monitors = sct.monitors
        raw = sct.grab(monitors[1] if len(monitors) > 1 else monitors[0])
        img = Image.frombytes("RGB", raw.size, raw.rgb)
    w, h = img.size
    scale = min(1.0, max_side / max(w, h))
    if scale < 1:
        img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue(), Screen(width=w, height=h)


def screenshot_save(path: str | None = None) -> str:
    jpeg, _ = screenshot_jpeg(max_side=1920, quality=85)
    target = Path(path).expanduser() if path else Path.home() / f"jarvis-{int(time.time())}.jpg"
    decision = inspect_path_write(str(target))
    if not decision.allowed:
        return decision.reason
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(jpeg)
    return f"screenshot em {target} ({len(jpeg)} bytes)"

from __future__ import annotations

import json
import time
from typing import Any, Callable

from jarvis.config import Settings
from jarvis.prompt import SYSTEM, observation_text
from jarvis.tools import TOOLS
from jarvis.xai import XAI, jpeg_data_url, parse_args

Log = Callable[[str], None]


def _log_default(line: str) -> None:
    print(line, flush=True)


def execute(name: str, args: dict[str, Any]) -> tuple[str, bool]:
    """Run a real OS action. Returns (result, changed_screen)."""
    if name == "wait":
        seconds = min(8.0, max(0.2, float(args.get("seconds") or 0.8)))
        time.sleep(seconds)
        return f"esperou {seconds:.1f}s", True
    if name not in {
        "mouse_move",
        "click",
        "drag",
        "scroll",
        "type_text",
        "hotkey",
        "press",
        "open_app",
        "open_url",
        "open_path",
        "list_dir",
        "read_file",
        "write_file",
        "run_command",
    }:
        return f"ferramenta desconhecida: {name}", False

    from jarvis import apps, computer

    if name == "mouse_move":
        return computer.move(float(args["x"]), float(args["y"]), float(args.get("duration") or 0.25)), True
    if name == "click":
        x = args.get("x")
        y = args.get("y")
        return (
            computer.click(
                None if x is None else float(x),
                None if y is None else float(y),
                str(args.get("button") or "left"),
                int(args.get("clicks") or 1),
            ),
            True,
        )
    if name == "drag":
        return computer.drag(float(args["x"]), float(args["y"])), True
    if name == "scroll":
        return computer.scroll(int(args["amount"])), True
    if name == "type_text":
        return computer.type_text(str(args.get("text") or "")), True
    if name == "hotkey":
        keys = args.get("keys") or []
        if isinstance(keys, str):
            keys = [k for k in keys.replace("+", " ").split() if k]
        return computer.hotkey(*[str(k) for k in keys]), True
    if name == "press":
        return computer.press(str(args.get("key") or "enter")), True
    if name == "open_app":
        return apps.open_app(str(args.get("name") or "")), True
    if name == "open_url":
        return apps.open_url(str(args.get("url") or "")), True
    if name == "open_path":
        return apps.open_path(str(args.get("path") or "")), True
    if name == "list_dir":
        return apps.list_dir(str(args.get("path") or ".")), False
    if name == "read_file":
        return apps.read_file(str(args.get("path") or "")), False
    if name == "write_file":
        return apps.write_file(str(args.get("path") or ""), str(args.get("content") or "")), False
    return apps.run_command(str(args.get("command") or "")), True


class Agent:
    def __init__(self, settings: Settings, log: Log = _log_default) -> None:
        self.settings = settings
        self.xai = XAI(settings)
        self.log = log
        self.messages: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM}]

    def _observe(self) -> dict[str, Any]:
        from jarvis import computer

        jpeg, scr = computer.screenshot_jpeg()
        return {
            "role": "user",
            "content": [
                {"type": "text", "text": observation_text(scr.width, scr.height)},
                {"type": "image_url", "image_url": {"url": jpeg_data_url(jpeg), "detail": "high"}},
            ],
        }

    def run(self, order: str) -> str:
        self.log(f"ordem: {order}")
        self.messages.append({"role": "user", "content": order})
        self.messages.append(self._observe())
        final = ""
        for step in range(self.settings.max_steps):
            message = self.xai.chat(self.messages, TOOLS)
            tool_calls = message.get("tool_calls") or []
            content = (message.get("content") or "").strip()
            if tool_calls:
                self.messages.append(
                    {
                        "role": "assistant",
                        "content": content or None,
                        "tool_calls": tool_calls,
                    }
                )
                saw_screen = False
                for call in tool_calls:
                    fn = call.get("function") or {}
                    name = fn.get("name") or ""
                    args = parse_args(fn.get("arguments") or "")
                    self.log(f"  → {name} {json.dumps(args, ensure_ascii=False)}")
                    result, changed = execute(name, args)
                    self.log(f"    {result.splitlines()[0][:180]}")
                    self.messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.get("id"),
                            "content": result[:6000],
                        }
                    )
                    saw_screen = saw_screen or changed
                if saw_screen:
                    time.sleep(0.25)
                    self.messages.append(self._observe())
                continue
            final = content or "Ordem concluída."
            self.messages.append({"role": "assistant", "content": final})
            self.log(final)
            return final
        final = "Limite de passos atingido. Interrompo aqui, senhor."
        self.log(final)
        return final

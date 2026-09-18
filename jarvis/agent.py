from __future__ import annotations

import json
import time
from typing import Any, Callable

from jarvis.config import Settings
from jarvis.prompt import CONTINUE, SYSTEM, observation_text
from jarvis.tools import TOOLS
from jarvis.xai import Brain, jpeg_data_url, parse_args

Log = Callable[[str], None]

OS_TOOLS = {
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
    "screenshot_save",
    "volume",
    "media",
}


def _log_default(line: str) -> None:
    print(line, flush=True)


def execute(name: str, args: dict[str, Any]) -> tuple[str, bool]:
    """Run a real OS action. Returns (result, changed_screen)."""
    if name == "done":
        return str(args.get("summary") or "ordem concluída").strip(), False
    if name == "wait":
        seconds = min(8.0, max(0.2, float(args.get("seconds") or 0.8)))
        time.sleep(seconds)
        return f"esperou {seconds:.1f}s", True
    if name == "clipboard_get":
        from jarvis.system import clipboard_get

        return clipboard_get(), False
    if name == "clipboard_set":
        from jarvis.system import clipboard_set

        return clipboard_set(str(args.get("text") or "")), False
    if name == "system_info":
        from jarvis.system import system_info

        return system_info(), False
    if name == "notify":
        from jarvis.system import notify

        return notify(str(args.get("title") or "J.A.R.V.I.S."), str(args.get("message") or "")), False
    if name == "fetch_url":
        from jarvis.net import fetch_text

        try:
            return fetch_text(str(args.get("url") or "")), False
        except ValueError as exc:
            return f"bloqueado: {exc}", False
    if name == "window_list":
        from jarvis.system import window_list

        return window_list(), False
    if name == "window_focus":
        from jarvis.system import window_focus

        return window_focus(str(args.get("title") or "")), True
    if name not in OS_TOOLS:
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
    if name == "screenshot_save":
        return computer.screenshot_save(args.get("path")), False
    if name == "volume":
        return computer.volume(str(args.get("action") or "")), False
    if name == "media":
        return computer.media(str(args.get("action") or "")), False
    return apps.run_command(str(args.get("command") or "")), True


class Agent:
    def __init__(self, settings: Settings, log: Log = _log_default) -> None:
        self.settings = settings
        self.brain = Brain(settings)
        self.xai = self.brain
        self.log = log
        self.messages: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM}]

    def _observe(self) -> dict[str, Any]:
        from jarvis import computer

        jpeg, scr = computer.screenshot_jpeg()
        caption = observation_text(scr.width, scr.height)
        if self.settings.provider == "nvidia":
            desc = self.brain.see(jpeg, caption)
            return {"role": "user", "content": desc}
        return {
            "role": "user",
            "content": [
                {"type": "text", "text": caption},
                {"type": "image_url", "image_url": {"url": jpeg_data_url(jpeg), "detail": "high"}},
            ],
        }

    def _compact(self, order: str) -> None:
        if len(self.messages) <= 22:
            return
        system = self.messages[0]
        self.messages = [
            system,
            {"role": "user", "content": f"Ordem em curso (não encerrar antes de done): {order}"},
            *self.messages[-18:],
        ]

    def run(self, order: str) -> str:
        self.log(f"[{self.settings.provider}] ordem: {order}")
        self.messages.append({"role": "user", "content": order})
        self.messages.append(self._observe())
        last_text = ""
        idle = 0
        acted_ever = False
        for step in range(self.settings.max_steps):
            self._compact(order)
            self.log(f"  passo {step + 1}/{self.settings.max_steps}")
            message = self.brain.chat(self.messages, TOOLS)
            tool_calls = message.get("tool_calls") or []
            content = (message.get("content") or "").strip()
            if content:
                last_text = content

            if tool_calls:
                idle = 0
                self.messages.append(
                    {
                        "role": "assistant",
                        "content": content or None,
                        "tool_calls": tool_calls,
                    }
                )
                done_summary: str | None = None
                acted = False
                for call in tool_calls:
                    fn = call.get("function") or {}
                    name = fn.get("name") or ""
                    args = parse_args(fn.get("arguments") or "")
                    self.log(f"  → {name} {json.dumps(args, ensure_ascii=False)}")
                    if name == "done":
                        done_summary = str(args.get("summary") or content or "Ordem concluída.").strip()
                        self.messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": call.get("id"),
                                "content": done_summary,
                            }
                        )
                        continue
                    result, changed = execute(name, args)
                    acted = True
                    acted_ever = True
                    self.log(f"    {result.splitlines()[0][:180]}")
                    self.messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.get("id"),
                            "content": result[:6000],
                        }
                    )
                    if changed:
                        time.sleep(0.28)
                if done_summary is not None and not acted:
                    self.log(done_summary)
                    return done_summary
                if done_summary is not None and acted:
                    time.sleep(0.2)
                    self.messages.append(self._observe())
                    self.messages.append(
                        {
                            "role": "user",
                            "content": (
                                "Você chamou done depois de agir. Confirme na tela se o pedido "
                                f"está 100% feito. Se sim, chame done de novo. Pedido: {order}"
                            ),
                        }
                    )
                    continue
                time.sleep(0.2)
                self.messages.append(self._observe())
                continue

            idle += 1
            if content:
                self.messages.append({"role": "assistant", "content": content})
                self.log(f"  (ainda não concluiu) {content[:160]}")
            if idle >= 2 and not acted_ever:
                final = last_text or "Pronto, senhor."
                self.log(final)
                return final
            self.messages.append({"role": "user", "content": CONTINUE.format(order=order)})
            self.messages.append(self._observe())

        final = last_text or "Limite de passos atingido. Interrompo aqui, senhor."
        self.log(final)
        return final

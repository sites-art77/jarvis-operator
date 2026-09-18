from __future__ import annotations

import argparse
import sys

from jarvis.agent import Agent
from jarvis.config import load_settings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="jarvis",
        description="J.A.R.V.I.S. local — vê a tela, move o mouse, clica e executa.",
    )
    parser.add_argument("order", nargs="*", help="Ordem em português. Vazio = REPL.")
    parser.add_argument("--voice", action="store_true", help="Escuta o microfone, executa, responde em voz.")
    parser.add_argument("--listen", type=float, default=5.0, help="Segundos de escuta no modo --voice.")
    args = parser.parse_args(argv)

    settings = load_settings()
    agent = Agent(settings)

    if args.voice:
        from jarvis.voice import listen_and_transcribe, speak

        print("Modo voz. Ctrl+C para sair. Mova o mouse ao canto para abortar um clique (failsafe).")
        try:
            while True:
                try:
                    text = listen_and_transcribe(agent.xai, args.listen)
                except Exception as exc:
                    print(f"transcrição falhou: {exc}")
                    continue
                if not text:
                    print("silêncio.")
                    continue
                print(f"você: {text}")
                reply = agent.run(text)
                try:
                    speak(settings, agent.xai, reply)
                except Exception as exc:
                    print(f"voz: {exc}")
        except KeyboardInterrupt:
            print("\naté logo, senhor.")
            return 0

    order = " ".join(args.order).strip()
    if order:
        agent.run(order)
        return 0

    print("J.A.R.V.I.S. online. Escreva uma ordem. 'sair' encerra.")
    print("Failsafe: arraste o mouse ao canto superior esquerdo para abortar.")
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not line:
            continue
        if line.lower() in {"sair", "exit", "quit"}:
            return 0
        try:
            agent.run(line)
        except Exception as exc:
            print(f"falha: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

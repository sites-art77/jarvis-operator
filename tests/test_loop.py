from jarvis.agent import Agent
from jarvis.config import Settings


def _settings(**kwargs) -> Settings:
    base = dict(
        provider="nvidia",
        api_key="x",
        api_base="http://example.invalid",
        model="nvidia/nemotron-3.5-lightning-30b-a3b",
        vision_model="nvidia/nemotron-nano-12b-v2-vl",
        lang="pt-BR",
        voice="altair",
        max_steps=8,
        xai_key="",
    )
    base.update(kwargs)
    return Settings(**base)


class ScriptedBrain:
    def __init__(self, script: list[dict]) -> None:
        self.script = script
        self.n = 0
        self.chats = 0

    def chat(self, messages, tools=None):
        self.chats += 1
        i = min(self.n, len(self.script) - 1)
        self.n += 1
        return self.script[i]

    def see(self, jpeg, caption):
        return caption


def test_text_only_does_not_stop_until_done():
    brain = ScriptedBrain(
        [
            {"content": "vou clicar no bloco de notas", "tool_calls": []},
            {
                "content": None,
                "tool_calls": [
                    {
                        "id": "c1",
                        "type": "function",
                        "function": {"name": "wait", "arguments": '{"seconds": 0.2}'},
                    }
                ],
            },
            {
                "content": None,
                "tool_calls": [
                    {
                        "id": "c2",
                        "type": "function",
                        "function": {"name": "done", "arguments": '{"summary": "pedido concluído"}'},
                    }
                ],
            },
        ]
    )
    agent = Agent(_settings(), log=lambda _line: None)
    agent.brain = brain
    agent._observe = lambda: {"role": "user", "content": "obs"}  # type: ignore[method-assign]
    out = agent.run("abra o bloco de notas")
    assert out == "pedido concluído"
    assert brain.chats == 3


def test_after_action_keeps_going_until_done():
    brain = ScriptedBrain(
        [
            {
                "content": None,
                "tool_calls": [
                    {
                        "id": "w",
                        "type": "function",
                        "function": {"name": "wait", "arguments": '{"seconds": 0.2}'},
                    }
                ],
            },
            {"content": "acho que já está", "tool_calls": []},
            {
                "content": None,
                "tool_calls": [
                    {
                        "id": "d",
                        "type": "function",
                        "function": {"name": "done", "arguments": '{"summary": "fechado"}'},
                    }
                ],
            },
        ]
    )
    agent = Agent(_settings(), log=lambda _line: None)
    agent.brain = brain
    agent._observe = lambda: {"role": "user", "content": "obs"}  # type: ignore[method-assign]
    out = agent.run("abra e feche o notepad")
    assert out == "fechado"
    assert brain.chats == 3


def test_pure_conversation_stops_after_second_text():
    brain = ScriptedBrain(
        [
            {"content": "boa tarde, senhor.", "tool_calls": []},
            {"content": "à sua disposição.", "tool_calls": []},
        ]
    )
    agent = Agent(_settings(max_steps=8), log=lambda _line: None)
    agent.brain = brain
    agent._observe = lambda: {"role": "user", "content": "obs"}  # type: ignore[method-assign]
    out = agent.run("olá")
    assert out == "à sua disposição."
    assert brain.chats == 2

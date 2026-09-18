from jarvis.xai import parse_args, parse_embedded_tools, strip_reasoning


def test_parse_object():
    assert parse_args('{"x": 10, "y": 20}') == {"x": 10, "y": 20}


def test_parse_empty():
    assert parse_args("") == {}
    assert parse_args("not-json") == {}


def test_embedded_tool_calls():
    raw = '<tool_call>{"name": "click", "arguments": {"x": 40, "y": 60}}</tool_call>'
    calls = parse_embedded_tools(raw)
    assert len(calls) == 1
    assert calls[0]["function"]["name"] == "click"
    assert '"x": 40' in calls[0]["function"]["arguments"]


def test_strip_think():
    assert strip_reasoning("<think>segredo</think>pronto") == "pronto"

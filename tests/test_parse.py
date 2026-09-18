from jarvis.xai import parse_args


def test_parse_object():
    assert parse_args('{"x": 10, "y": 20}') == {"x": 10, "y": 20}


def test_parse_empty():
    assert parse_args("") == {}
    assert parse_args("not-json") == {}

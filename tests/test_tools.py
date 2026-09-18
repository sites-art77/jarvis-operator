from jarvis.agent import execute
from jarvis.tools import TOOL_NAMES, TOOLS


def test_tool_catalog_covers_computer_use():
    expected = {
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
        "wait",
    }
    assert set(TOOL_NAMES) == expected
    assert all(item["type"] == "function" for item in TOOLS)


def test_unknown_tool_does_not_touch_os():
    result, changed = execute("teleport", {})
    assert "desconhecida" in result
    assert changed is False


def test_wait_clamps_duration():
    result, changed = execute("wait", {"seconds": 0.2})
    assert result.startswith("esperou")
    assert changed is True

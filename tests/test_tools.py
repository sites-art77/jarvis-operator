from jarvis.agent import OS_TOOLS, execute
from jarvis.tools import TOOL_NAMES, TOOLS

WIRED = set(OS_TOOLS) | {
    "wait",
    "clipboard_get",
    "clipboard_set",
    "system_info",
    "notify",
    "fetch_url",
    "window_list",
    "window_focus",
}


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
        "fetch_url",
        "open_path",
        "list_dir",
        "read_file",
        "write_file",
        "run_command",
        "clipboard_get",
        "clipboard_set",
        "screenshot_save",
        "system_info",
        "notify",
        "volume",
        "media",
        "window_list",
        "window_focus",
        "wait",
    }
    assert set(TOOL_NAMES) == expected
    assert set(TOOL_NAMES) == WIRED
    assert all(item["type"] == "function" for item in TOOLS)


def test_unknown_tool_does_not_touch_os():
    result, changed = execute("teleport", {})
    assert "desconhecida" in result
    assert changed is False


def test_wait_clamps_duration():
    result, changed = execute("wait", {"seconds": 0.2})
    assert result.startswith("esperou")
    assert changed is True


def test_system_info_is_real():
    result, changed = execute("system_info", {})
    assert "so:" in result
    assert changed is False


def test_fetch_blocks_localhost():
    result, changed = execute("fetch_url", {"url": "http://127.0.0.1/secret"})
    assert "bloqueado" in result
    assert changed is False

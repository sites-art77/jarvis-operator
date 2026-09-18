from jarvis.safety import inspect_command, inspect_path_write


def test_blocks_disk_wipe():
    d = inspect_command("rm -rf /")
    assert d.allowed is False
    assert d.needs_confirm is True


def test_blocks_fork_bomb():
    d = inspect_command(":(){ :|:& };:")
    assert d.allowed is False


def test_blocks_shutdown():
    d = inspect_command("sudo shutdown -h now")
    assert d.allowed is False


def test_confirms_recursive_delete():
    d = inspect_command("rm -rf ./build")
    assert d.allowed is True
    assert d.needs_confirm is True


def test_allows_ls():
    d = inspect_command("ls -la")
    assert d.allowed is True
    assert d.needs_confirm is False


def test_blocks_windows_system_write():
    d = inspect_path_write("C:/Windows/System32/hack.dll")
    assert d.allowed is False


def test_allows_home_write():
    d = inspect_path_write("/home/user/notes/agenda.md")
    assert d.allowed is True

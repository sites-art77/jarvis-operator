import pytest

from jarvis.net import assert_public_http_url


def test_rejects_file_scheme():
    with pytest.raises(ValueError):
        assert_public_http_url("file:///etc/passwd")


def test_rejects_localhost():
    with pytest.raises(ValueError):
        assert_public_http_url("http://localhost:8080/admin")


def test_rejects_private_ip():
    with pytest.raises(ValueError):
        assert_public_http_url("http://192.168.0.1/")


def test_accepts_https():
    assert assert_public_http_url("https://example.com/path") == "https://example.com/path"

import pytest

from etoropy.config.constants import (
    API_PREFIX,
    DEFAULT_BASE_URL,
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_TIMEOUT,
    DEFAULT_WS_URL,
)
from etoropy.config.settings import EToroConfig


def test_constants() -> None:
    assert API_PREFIX == "/api/v1"
    assert DEFAULT_BASE_URL == "https://public-api.etoro.com"
    assert DEFAULT_WS_URL == "wss://ws.etoro.com/ws"
    assert DEFAULT_TIMEOUT == 30.0
    assert DEFAULT_RETRY_ATTEMPTS == 3


def test_config_explicit() -> None:
    config = EToroConfig(
        api_key="my-api-key",
        user_key="my-user-key",
        mode="real",
        timeout=60.0,
    )
    assert config.api_key == "my-api-key"
    assert config.user_key == "my-user-key"
    assert config.mode == "real"
    assert config.timeout == 60.0
    assert config.base_url == DEFAULT_BASE_URL
    assert config.ws_url == DEFAULT_WS_URL


def test_config_defaults() -> None:
    config = EToroConfig(api_key="key", user_key="ukey")
    assert config.mode == "demo"
    assert config.retry_attempts == 3
    assert config.retry_delay == 1.0


def test_config_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ETORO_API_KEY", "env-api-key")
    monkeypatch.setenv("ETORO_USER_KEY", "env-user-key")
    monkeypatch.setenv("ETORO_MODE", "real")
    config = EToroConfig()
    assert config.api_key == "env-api-key"
    assert config.user_key == "env-user-key"
    assert config.mode == "real"

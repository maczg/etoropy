from __future__ import annotations

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings

from .constants import (
    DEFAULT_BASE_URL,
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_RETRY_DELAY,
    DEFAULT_TIMEOUT,
    DEFAULT_WS_URL,
)


class EToroConfig(BaseSettings):
    """SDK configuration, loaded from environment variables or passed directly.

    Every field can be set via its ``ETORO_``-prefixed env var
    (e.g. ``ETORO_API_KEY``, ``ETORO_MODE``).

    Attributes:
        api_key: eToro Public API key.
        user_key: eToro user key.
        mode: ``"demo"`` (paper trading) or ``"real"`` (live trading).
        base_url: REST API base URL.
        ws_url: WebSocket endpoint URL.
        timeout: HTTP request timeout in seconds.
        retry_attempts: Max retries on transient failures (0 = no retry).
        retry_delay: Base delay in seconds between retries.
    """

    model_config = {"env_prefix": "ETORO_"}

    api_key: str = Field(min_length=1, description="eToro API key")
    user_key: str = Field(min_length=1, description="eToro user key")
    mode: Literal["demo", "real"] = "demo"
    base_url: str = DEFAULT_BASE_URL
    ws_url: str = DEFAULT_WS_URL
    timeout: float = DEFAULT_TIMEOUT
    retry_attempts: int = Field(default=DEFAULT_RETRY_ATTEMPTS, ge=0)
    retry_delay: float = Field(default=DEFAULT_RETRY_DELAY, gt=0)

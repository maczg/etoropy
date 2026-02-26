from __future__ import annotations

import pytest

from etoropy.config.settings import EToroConfig
from etoropy.http.client import HttpClient


@pytest.fixture
def config() -> EToroConfig:
    return EToroConfig(
        api_key="test-api-key",
        user_key="test-user-key",
        mode="demo",
    )


@pytest.fixture
def http_client(config: EToroConfig) -> HttpClient:
    return HttpClient(config, rate_limiter=False)

import asyncio

import pytest

from etoropy.config.settings import EToroConfig
from etoropy.http.client import HttpClient
from etoropy.http.rate_limiter import RateLimiter, RateLimiterOptions


@pytest.mark.asyncio
async def test_acquire_under_limit() -> None:
    limiter = RateLimiter(RateLimiterOptions(max_requests=5, window_s=10.0))
    for _ in range(5):
        await limiter.acquire()
    assert limiter.current_usage == 5


@pytest.mark.asyncio
async def test_penalize() -> None:
    limiter = RateLimiter(RateLimiterOptions(max_requests=20, window_s=10.0))
    limiter.penalize(0.1)
    assert limiter.is_penalized
    await asyncio.sleep(0.15)
    assert not limiter.is_penalized


@pytest.mark.asyncio
async def test_dispose() -> None:
    limiter = RateLimiter()
    await limiter.acquire()
    limiter.dispose()
    # Should not raise after dispose
    await limiter.acquire()


def test_http_client_uses_config_rate_limit_values() -> None:
    config = EToroConfig(
        api_key="k",
        user_key="u",
        rate_limit_max_requests=5,
        rate_limit_window=2.0,
    )
    client = HttpClient(config)
    assert client._rate_limiter is not None
    assert client._rate_limiter._max_requests == 5
    assert client._rate_limiter._window_s == 2.0


def test_http_client_rate_limit_disabled_via_config() -> None:
    config = EToroConfig(
        api_key="k",
        user_key="u",
        rate_limit=False,
    )
    client = HttpClient(config)
    assert client._rate_limiter is None


def test_http_client_explicit_options_override_config() -> None:
    config = EToroConfig(
        api_key="k",
        user_key="u",
        rate_limit_max_requests=5,
        rate_limit_window=2.0,
    )
    opts = RateLimiterOptions(max_requests=50, window_s=30.0)
    client = HttpClient(config, rate_limiter=opts)
    assert client._rate_limiter is not None
    assert client._rate_limiter._max_requests == 50
    assert client._rate_limiter._window_s == 30.0

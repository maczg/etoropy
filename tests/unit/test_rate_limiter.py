import asyncio

import pytest

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

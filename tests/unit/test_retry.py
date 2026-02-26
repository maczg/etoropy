import pytest

from etoropy.http.retry import RetryOptions, retry


@pytest.mark.asyncio
async def test_retry_succeeds_first_try() -> None:
    call_count = 0

    async def fn() -> str:
        nonlocal call_count
        call_count += 1
        return "ok"

    result = await retry(fn, RetryOptions(attempts=3, delay=0.01))
    assert result == "ok"
    assert call_count == 1


@pytest.mark.asyncio
async def test_retry_succeeds_after_failures() -> None:
    call_count = 0

    async def fn() -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("fail")
        return "ok"

    result = await retry(
        fn,
        RetryOptions(
            attempts=3,
            delay=0.01,
            should_retry=lambda e: isinstance(e, ValueError),
        ),
    )
    assert result == "ok"
    assert call_count == 3


@pytest.mark.asyncio
async def test_retry_exhausts_attempts() -> None:
    async def fn() -> str:
        raise ValueError("always fails")

    with pytest.raises(ValueError, match="always fails"):
        await retry(
            fn,
            RetryOptions(
                attempts=2,
                delay=0.01,
                should_retry=lambda e: isinstance(e, ValueError),
            ),
        )


@pytest.mark.asyncio
async def test_retry_no_retry_on_non_retryable() -> None:
    call_count = 0

    async def fn() -> str:
        nonlocal call_count
        call_count += 1
        raise TypeError("not retryable")

    with pytest.raises(TypeError):
        await retry(
            fn,
            RetryOptions(
                attempts=3,
                delay=0.01,
                should_retry=lambda e: isinstance(e, ValueError),
            ),
        )
    assert call_count == 1

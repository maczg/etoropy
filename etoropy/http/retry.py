from __future__ import annotations

import asyncio
import random
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

T = TypeVar("T")


@dataclass
class RetryOptions:
    """Configuration for the ``retry()`` helper.

    Attributes:
        attempts: Maximum number of tries (including the first).
        delay: Base delay in seconds before the first retry.
        backoff_multiplier: Multiplied to the delay after each attempt.
        jitter: If True, adds +/-25% random jitter to the computed delay.
        should_retry: Predicate that receives the exception and returns
            True if the request should be retried.
        get_retry_after_s: Optional callback that extracts a server-supplied
            retry-after delay from the exception (e.g. from a 429 response).
        on_retry: Optional callback fired before each retry sleep, receiving
            (attempt_number, wait_seconds, exception).
    """

    attempts: int = 3
    delay: float = 1.0  # seconds
    backoff_multiplier: float = 2.0
    jitter: bool = True
    should_retry: Callable[[BaseException], bool] = field(default=lambda: lambda _: False)
    get_retry_after_s: Callable[[BaseException], float | None] | None = None
    on_retry: Callable[[int, float, BaseException], None] | None = None


def _apply_jitter(s: float) -> float:
    jitter_range = s * 0.25
    return s + (random.random() * 2 - 1) * jitter_range  # noqa: S311


async def retry(fn: Callable[[], Any], options: RetryOptions) -> Any:
    """Execute ``fn`` with automatic retries on failure.

    Uses exponential backoff (``delay * backoff_multiplier ** attempt``)
    with optional jitter.  Honors server-supplied ``Retry-After`` values
    when ``get_retry_after_s`` is provided.
    """
    last_error: BaseException | None = None

    for attempt in range(options.attempts):
        try:
            return await fn()  # type: ignore[misc]
        except Exception as error:
            last_error = error
            if attempt < options.attempts - 1 and options.should_retry(error):
                retry_after = options.get_retry_after_s(error) if options.get_retry_after_s else None
                backoff = options.delay * (options.backoff_multiplier**attempt)
                wait_s = retry_after if retry_after is not None else backoff

                if options.jitter and retry_after is None:
                    wait_s = _apply_jitter(wait_s)

                if options.on_retry:
                    options.on_retry(attempt + 1, wait_s, error)

                await asyncio.sleep(wait_s)
                continue
            raise

    raise last_error  # type: ignore[misc]

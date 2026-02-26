from __future__ import annotations

import asyncio
import time
from collections import deque
from dataclasses import dataclass


@dataclass
class RateLimiterOptions:
    max_requests: int = 20
    window_s: float = 10.0


class RateLimiter:
    """Token-bucket rate limiter for outgoing HTTP requests.

    Tracks request timestamps in a sliding window (default: 20 requests
    per 10 seconds).  ``acquire()`` blocks the caller when the bucket is
    full until a slot opens.

    On HTTP 429 responses, call ``penalize(retry_after_s)`` to force all
    subsequent requests to wait for the server-specified back-off period.
    """

    def __init__(self, options: RateLimiterOptions | None = None) -> None:
        opts = options or RateLimiterOptions()
        self._max_requests = opts.max_requests
        self._window_s = opts.window_s
        self._timestamps: deque[float] = deque()
        self._penalty_until: float = 0.0
        self._lock = asyncio.Lock()
        self._disposed = False

    async def acquire(self) -> None:
        if self._disposed:
            return

        async with self._lock:
            now = time.monotonic()
            if self._penalty_until > now:
                await asyncio.sleep(self._penalty_until - now)

            self._prune_timestamps()

            if len(self._timestamps) < self._max_requests:
                self._timestamps.append(time.monotonic())
                return

            # Wait until the oldest timestamp expires
            wait_s = self._timestamps[0] + self._window_s - time.monotonic() + 0.001
            if wait_s > 0:
                await asyncio.sleep(wait_s)

            self._prune_timestamps()
            self._timestamps.append(time.monotonic())

    def penalize(self, retry_after_s: float) -> None:
        until = time.monotonic() + retry_after_s
        if until > self._penalty_until:
            self._penalty_until = until

    @property
    def queue_size(self) -> int:
        return 0  # simplified — lock-based instead of queue-based

    @property
    def current_usage(self) -> int:
        self._prune_timestamps()
        return len(self._timestamps)

    @property
    def is_penalized(self) -> bool:
        return time.monotonic() < self._penalty_until

    def dispose(self) -> None:
        self._disposed = True
        self._timestamps.clear()

    def _prune_timestamps(self) -> None:
        cutoff = time.monotonic() - self._window_s
        while self._timestamps and self._timestamps[0] < cutoff:
            self._timestamps.popleft()

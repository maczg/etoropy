from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

import httpx

from .._utils import generate_uuid
from ..config.settings import EToroConfig
from ..errors.exceptions import (
    EToroApiError,
    EToroAuthError,
    EToroRateLimitError,
    RequestContext,
)
from .rate_limiter import RateLimiter, RateLimiterOptions
from .retry import RetryOptions, retry

logger = logging.getLogger("etoropy")


@dataclass
class RequestOptions:
    method: str
    path: str
    query: dict[str, str | int | bool | None] | None = None
    body: Any = None
    request_id: str | None = None


class HttpClient:
    """Async HTTP client wrapping ``httpx.AsyncClient``.

    Every request automatically includes ``x-api-key`` and ``x-user-key``
    auth headers, passes through the token-bucket rate limiter, and is
    retried on transient failures (5xx, 429, connection errors) with
    exponential backoff and jitter.

    Pydantic ``BaseModel`` request bodies are serialized with
    ``model_dump(by_alias=True, exclude_none=True)`` so PascalCase field
    aliases are preserved for the eToro API.
    """

    def __init__(
        self,
        config: EToroConfig,
        *,
        rate_limiter: RateLimiterOptions | None | bool = None,
    ) -> None:
        self._config = config
        self._client = httpx.AsyncClient(timeout=config.timeout)

        if rate_limiter is False or not config.rate_limit:
            self._rate_limiter: RateLimiter | None = None
        elif isinstance(rate_limiter, RateLimiterOptions):
            self._rate_limiter = RateLimiter(rate_limiter)
        else:
            self._rate_limiter = RateLimiter(
                RateLimiterOptions(
                    max_requests=config.rate_limit_max_requests,
                    window_s=config.rate_limit_window,
                )
            )

    async def request(self, options: RequestOptions, response_type: type | None = None) -> Any:
        request_id = options.request_id or generate_uuid()
        start_time = time.monotonic()

        async def _do_request() -> Any:
            if self._rate_limiter:
                await self._rate_limiter.acquire()
            return await self._execute_request(options, request_id, start_time)

        return await retry(
            _do_request,
            RetryOptions(
                attempts=self._config.retry_attempts,
                delay=self._config.retry_delay,
                jitter=True,
                should_retry=self._is_retryable,
                get_retry_after_s=self._get_retry_after,
                on_retry=lambda attempt, wait_s, error: logger.warning(
                    "Retrying %s %s (attempt %d, waiting %.1fs): %s",
                    options.method,
                    options.path,
                    attempt,
                    wait_s,
                    error,
                ),
            ),
        )

    async def _execute_request(
        self,
        options: RequestOptions,
        request_id: str,
        start_time: float,
    ) -> Any:
        url = self._build_url(options.path, options.query)

        headers: dict[str, str] = {
            "x-request-id": request_id,
            "x-api-key": self._config.api_key,
            "x-user-key": self._config.user_key,
        }

        if options.body is not None:
            headers["Content-Type"] = "application/json"

        json_body = None
        if options.body is not None:
            from pydantic import BaseModel

            if isinstance(options.body, BaseModel):
                json_body = options.body.model_dump(by_alias=True, exclude_none=True)
            elif isinstance(options.body, dict):
                json_body = options.body
            else:
                json_body = options.body

        logger.debug("%s %s", options.method, url)

        response = await self._client.request(
            method=options.method,
            url=url,
            headers=headers,
            json=json_body,
        )

        duration_s = time.monotonic() - start_time

        if response.status_code == 204:
            return None

        if response.status_code in (401, 403):
            raise EToroAuthError(
                f"Authentication failed ({response.status_code})",
                request_id=request_id,
            )

        if response.status_code == 429:
            retry_after_header = response.headers.get("Retry-After")
            retry_after_s = float(retry_after_header) if retry_after_header else None
            if retry_after_s is not None and self._rate_limiter:
                self._rate_limiter.penalize(retry_after_s)
            raise EToroRateLimitError(
                "Rate limit exceeded",
                retry_after_s=retry_after_s,
                request_id=request_id,
            )

        if not response.is_success:
            body = response.text
            raise EToroApiError(
                f"API request failed: {response.status_code} {response.reason_phrase}"
                f" | {options.method} {url} | {body[:200] if body else ''}",
                status_code=response.status_code,
                response_body=body,
                request_id=request_id,
                request_context=RequestContext(
                    method=options.method,
                    path=options.path,
                    duration_s=duration_s,
                ),
            )

        text = response.text
        if not text:
            return None

        return response.json()

    def _is_retryable(self, error: BaseException) -> bool:
        if isinstance(error, EToroRateLimitError):
            return True
        if isinstance(error, EToroApiError) and error.status_code >= 500:
            return True
        return isinstance(error, (httpx.ConnectError, httpx.ReadTimeout))

    def _get_retry_after(self, error: BaseException) -> float | None:
        if isinstance(error, EToroRateLimitError) and error.retry_after_s:
            return error.retry_after_s
        return None

    def _build_url(self, path: str, query: dict[str, str | int | bool | None] | None) -> str:
        url = f"{self._config.base_url}{path}"
        if query:
            params = {k: str(v) for k, v in query.items() if v is not None}
            if params:
                qs = "&".join(f"{k}={v}" for k, v in params.items())
                url = f"{url}?{qs}"
        return url

    async def aclose(self) -> None:
        if self._rate_limiter:
            self._rate_limiter.dispose()
        await self._client.aclose()

    async def __aenter__(self) -> HttpClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class EToroError(Exception):
    """Base exception for all etoropy errors."""

    def __init__(self, message: str, cause: BaseException | None = None) -> None:
        super().__init__(message)
        self.__cause__ = cause


@dataclass(frozen=True)
class RequestContext:
    method: str
    path: str
    duration_s: float


class EToroApiError(EToroError):
    """HTTP error from the eToro API (4xx/5xx).

    Attributes:
        status_code: HTTP status code.
        response_body: Raw response text.
        request_id: Correlation ID sent with the request.
        request_context: Method, path, and duration of the failed request.
    """

    def __init__(
        self,
        message: str,
        status_code: int,
        response_body: Any = None,
        request_id: str | None = None,
        request_context: RequestContext | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body
        self.request_id = request_id
        self.request_context = request_context


class EToroAuthError(EToroError):
    """Authentication failure (HTTP 401/403 or WebSocket auth rejection)."""

    def __init__(self, message: str = "Authentication failed", request_id: str | None = None) -> None:
        super().__init__(message)
        self.request_id = request_id


class EToroRateLimitError(EToroApiError):
    """HTTP 429 -- rate limit exceeded.

    Attributes:
        retry_after_s: Seconds to wait before retrying (from ``Retry-After`` header).
    """

    def __init__(
        self,
        message: str,
        retry_after_s: float | None = None,
        request_id: str | None = None,
    ) -> None:
        super().__init__(message, 429, request_id=request_id)
        self.retry_after_s = retry_after_s


class EToroValidationError(EToroError):
    """Client-side validation error (e.g. unknown symbol, too many candles)."""

    def __init__(self, message: str, field: str | None = None) -> None:
        super().__init__(message)
        self.field = field


class EToroWebSocketError(EToroError):
    """WebSocket connection or protocol error."""

    def __init__(self, message: str, error_code: str | None = None) -> None:
        super().__init__(message)
        self.error_code = error_code

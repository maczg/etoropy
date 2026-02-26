from etoropy.errors.exceptions import (
    EToroApiError,
    EToroAuthError,
    EToroError,
    EToroRateLimitError,
    EToroValidationError,
    EToroWebSocketError,
    RequestContext,
)


def test_etoro_error() -> None:
    err = EToroError("Something went wrong")
    assert str(err) == "Something went wrong"
    assert isinstance(err, Exception)


def test_etoro_error_with_cause() -> None:
    cause = ValueError("original")
    err = EToroError("Wrapped error", cause=cause)
    assert err.__cause__ is cause


def test_api_error() -> None:
    err = EToroApiError(
        "Bad request",
        status_code=400,
        response_body='{"error": "invalid"}',
        request_id="req-123",
        request_context=RequestContext(method="POST", path="/api/v1/test", duration_s=0.5),
    )
    assert err.status_code == 400
    assert err.request_id == "req-123"
    assert err.request_context is not None
    assert err.request_context.method == "POST"
    assert isinstance(err, EToroError)


def test_auth_error() -> None:
    err = EToroAuthError()
    assert str(err) == "Authentication failed"
    assert isinstance(err, EToroError)


def test_rate_limit_error() -> None:
    err = EToroRateLimitError("Too many requests", retry_after_s=10.0)
    assert err.status_code == 429
    assert err.retry_after_s == 10.0
    assert isinstance(err, EToroApiError)


def test_validation_error() -> None:
    err = EToroValidationError("Invalid field", field="instrumentId")
    assert err.field == "instrumentId"
    assert isinstance(err, EToroError)


def test_websocket_error() -> None:
    err = EToroWebSocketError("Connection lost", error_code="ConnectionReset")
    assert err.error_code == "ConnectionReset"
    assert isinstance(err, EToroError)

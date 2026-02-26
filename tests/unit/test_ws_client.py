from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from etoropy.errors.exceptions import EToroAuthError, EToroWebSocketError
from etoropy.ws.client import WsClient, WsClientOptions


def _make_client(**overrides: object) -> WsClient:
    opts = WsClientOptions(
        api_key="test-api-key",
        user_key="test-user-key",
        auth_timeout=0.5,
        heartbeat_interval=0,
        heartbeat_timeout=0,
        reconnect_attempts=0,
        reconnect_delay=0.01,
        **overrides,  # type: ignore[arg-type]
    )
    return WsClient(opts)


# ── event emitter ────────────────────────────────────────────────────


def test_on_and_emit() -> None:
    ws = _make_client()
    received: list[int] = []
    ws.on("ping", lambda v: received.append(v))
    ws._emit("ping", 42)
    assert received == [42]


def test_off_removes_handler() -> None:
    ws = _make_client()
    received: list[int] = []
    handler = lambda v: received.append(v)
    ws.on("ping", handler)
    ws.off("ping", handler)
    ws._emit("ping", 1)
    assert received == []


def test_once_fires_only_once() -> None:
    ws = _make_client()
    received: list[int] = []
    ws.once("ping", lambda v: received.append(v))
    ws._emit("ping", 1)
    ws._emit("ping", 2)
    assert received == [1]


def test_remove_all_listeners() -> None:
    ws = _make_client()
    received: list[int] = []
    ws.on("a", lambda: received.append(1))
    ws.on("b", lambda: received.append(2))
    ws.remove_all_listeners()
    ws._emit("a")
    ws._emit("b")
    assert received == []


def test_remove_listeners_for_event() -> None:
    ws = _make_client()
    received: list[str] = []
    ws.on("a", lambda: received.append("a"))
    ws.on("b", lambda: received.append("b"))
    ws.remove_all_listeners("a")
    ws._emit("a")
    ws._emit("b")
    assert received == ["b"]


# ── _handle_message ──────────────────────────────────────────────────


def test_handle_auth_success() -> None:
    ws = _make_client()
    authenticated: list[bool] = []
    ws.on("authenticated", lambda: authenticated.append(True))

    ws._handle_message(json.dumps({"operation": "Authenticate"}))

    assert ws.is_authenticated is True
    assert authenticated == [True]


def test_handle_auth_error() -> None:
    ws = _make_client()
    errors: list[Exception] = []
    ws.on("error", lambda err: errors.append(err))

    ws._handle_message(json.dumps({"operation": "Authenticate", "errorCode": "INVALID_KEY"}))

    assert ws.is_authenticated is False
    assert len(errors) == 1
    assert isinstance(errors[0], EToroAuthError)


def test_handle_malformed_message_does_not_raise() -> None:
    ws = _make_client()
    ws._handle_message("not valid json {{{")


# ── connect / authenticate ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_connect_starts_receive_loop_before_auth() -> None:
    """The receive loop must be running before _authenticate waits,
    otherwise the auth response is never processed (deadlock)."""
    ws = _make_client()
    call_order: list[str] = []

    original_authenticate = ws._authenticate

    async def fake_ws_connect(*_a: object, **_kw: object) -> AsyncMock:
        mock_conn = AsyncMock()
        mock_conn.state = MagicMock()
        mock_conn.state.name = "OPEN"
        return mock_conn

    async def tracking_authenticate() -> None:
        # By the time authenticate is called, receive_task must already exist
        assert ws._receive_task is not None, "receive loop must start before authenticate"
        call_order.append("authenticate")
        # Simulate successful auth
        ws._authenticated = True
        ws._emit("authenticated")

    with patch("websockets.asyncio.client.connect", side_effect=fake_ws_connect):
        ws._authenticate = tracking_authenticate  # type: ignore[assignment]
        # _receive_loop will fail because mock ws doesn't iterate,
        # but that's fine — we just need to verify ordering
        ws._receive_loop = AsyncMock()  # type: ignore[assignment]
        await ws.connect()

    assert call_order == ["authenticate"]


@pytest.mark.asyncio
async def test_connect_authenticates_via_receive_loop() -> None:
    """Full integration: connect sends auth, receive loop processes the
    response, and connect() resolves."""
    ws = _make_client()

    auth_response = json.dumps({"operation": "Authenticate"})

    async def fake_ws_iter(self: object) -> object:  # noqa: ANN001
        yield auth_response

    mock_conn = AsyncMock()
    mock_conn.state = MagicMock()
    mock_conn.state.name = "OPEN"
    mock_conn.send = AsyncMock()
    mock_conn.__aiter__ = fake_ws_iter
    mock_conn.close = AsyncMock()

    async def fake_connect(*_a: object, **_kw: object) -> AsyncMock:
        return mock_conn

    with patch("websockets.asyncio.client.connect", side_effect=fake_connect):
        await ws.connect()

    assert ws.is_authenticated is True


@pytest.mark.asyncio
async def test_auth_timeout_raises() -> None:
    opts = WsClientOptions(
        api_key="test-api-key",
        user_key="test-user-key",
        auth_timeout=0.1,
        heartbeat_interval=0,
        heartbeat_timeout=0,
        reconnect_attempts=0,
    )
    ws = WsClient(opts)

    async def fake_ws_iter(self: object) -> object:  # noqa: ANN001
        # Never yield an auth response — simulate timeout
        await asyncio.sleep(10)
        return
        yield  # noqa: RET504  # make it an async generator

    mock_conn = AsyncMock()
    mock_conn.state = MagicMock()
    mock_conn.state.name = "OPEN"
    mock_conn.send = AsyncMock()
    mock_conn.__aiter__ = fake_ws_iter
    mock_conn.close = AsyncMock()

    async def fake_connect(*_a: object, **_kw: object) -> AsyncMock:
        return mock_conn

    with patch("websockets.asyncio.client.connect", side_effect=fake_connect):
        with pytest.raises(EToroAuthError, match="timed out"):
            await ws.connect()


# ── _receive_loop: binary message handling ───────────────────────────


@pytest.mark.asyncio
async def test_receive_loop_skips_binary_messages() -> None:
    ws = _make_client()
    received_messages: list[str] = []
    original_handle = ws._handle_message

    def tracking_handle(data: str) -> None:
        received_messages.append(data)
        original_handle(data)

    ws._handle_message = tracking_handle  # type: ignore[assignment]

    text_msg = json.dumps({"operation": "Authenticate"})

    async def fake_ws_iter(self: object) -> object:  # noqa: ANN001
        yield b"\x00"
        yield text_msg
        yield b"\x01\x02\x03"

    mock_conn = AsyncMock()
    mock_conn.__aiter__ = fake_ws_iter
    ws._ws = mock_conn

    await ws._receive_loop()

    assert received_messages == [text_msg]


@pytest.mark.asyncio
async def test_receive_loop_processes_text_messages() -> None:
    ws = _make_client()
    auth_events: list[bool] = []
    ws.on("authenticated", lambda: auth_events.append(True))

    text_msg = json.dumps({"operation": "Authenticate"})

    async def fake_ws_iter(self: object) -> object:  # noqa: ANN001
        yield text_msg

    mock_conn = AsyncMock()
    mock_conn.__aiter__ = fake_ws_iter
    ws._ws = mock_conn

    await ws._receive_loop()

    assert auth_events == [True]
    assert ws.is_authenticated is True


# ── disconnect ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_disconnect_cleans_up() -> None:
    ws = _make_client()

    mock_conn = AsyncMock()
    mock_conn.close = AsyncMock()
    ws._ws = mock_conn
    ws._authenticated = True
    ws._receive_task = asyncio.create_task(asyncio.sleep(10))

    await ws.disconnect()

    assert ws._ws is None
    assert ws.is_authenticated is False
    assert ws._receive_task is None
    mock_conn.close.assert_awaited_once()


# ── _send ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_send_raises_when_not_connected() -> None:
    ws = _make_client()
    with pytest.raises(EToroWebSocketError, match="not connected"):
        await ws._send({"test": True})
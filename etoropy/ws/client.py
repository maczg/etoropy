from __future__ import annotations

import asyncio
import contextlib
import json
import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import websockets
import websockets.asyncio.client

from .._utils import generate_uuid
from ..config.constants import (
    DEFAULT_WS_AUTH_TIMEOUT,
    DEFAULT_WS_HEARTBEAT_INTERVAL,
    DEFAULT_WS_HEARTBEAT_TIMEOUT,
    DEFAULT_WS_RECONNECT_ATTEMPTS,
    DEFAULT_WS_RECONNECT_DELAY,
    DEFAULT_WS_URL,
)
from ..errors.exceptions import EToroAuthError, EToroWebSocketError
from ..models.websocket import WsEnvelope
from .message_parser import parse_messages
from .subscription import WsSubscriptionTracker

logger = logging.getLogger("etoropy")


@dataclass
class WsClientOptions:
    api_key: str = ""
    user_key: str = ""
    ws_url: str = DEFAULT_WS_URL
    reconnect_attempts: int = DEFAULT_WS_RECONNECT_ATTEMPTS
    reconnect_delay: float = DEFAULT_WS_RECONNECT_DELAY
    auth_timeout: float = DEFAULT_WS_AUTH_TIMEOUT
    heartbeat_interval: float = DEFAULT_WS_HEARTBEAT_INTERVAL
    heartbeat_timeout: float = DEFAULT_WS_HEARTBEAT_TIMEOUT


EventHandler = Callable[..., Any]


class WsClient:
    """Low-level WebSocket client for the eToro streaming API.

    Handles authentication, automatic reconnection with exponential backoff,
    heartbeat (via the ``websockets`` library's built-in ``ping_interval``),
    and topic subscription tracking.

    Message dispatch uses a lightweight event-emitter pattern:
    ``on()`` / ``off()`` / ``once()`` / ``_emit()``.

    Emitted events::

        "open"           -> ()                     # TCP connection established
        "authenticated"  -> ()                     # auth handshake succeeded
        "message"        -> (WsEnvelope)           # raw data envelope
        "instrument:rate"-> (instrument_id, WsInstrumentRate)
        "private:event"  -> (WsPrivateEvent)       # order status changes
        "close"          -> (code, reason)          # connection closed
        "error"          -> (Exception)
    """

    def __init__(self, options: WsClientOptions) -> None:
        self._api_key = options.api_key
        self._user_key = options.user_key
        self._ws_url = options.ws_url
        self._max_reconnect_attempts = options.reconnect_attempts
        self._reconnect_delay = options.reconnect_delay
        self._auth_timeout = options.auth_timeout
        self._heartbeat_interval = options.heartbeat_interval
        self._heartbeat_timeout = options.heartbeat_timeout

        self._ws: websockets.asyncio.client.ClientConnection | None = None
        self._authenticated = False
        self._subscriptions = WsSubscriptionTracker()
        self._reconnect_attempts = 0
        self._intentional_close = False
        self._receive_task: asyncio.Task[None] | None = None
        self._heartbeat_task: asyncio.Task[None] | None = None
        self._last_pong_at: float = 0.0

        # Event listeners: event_name -> list of callbacks
        self._listeners: dict[str, list[EventHandler]] = {}

    # --- Event Emitter ---

    def on(self, event: str, handler: EventHandler) -> WsClient:
        self._listeners.setdefault(event, []).append(handler)
        return self

    def off(self, event: str, handler: EventHandler) -> WsClient:
        handlers = self._listeners.get(event)
        if handlers and handler in handlers:
            handlers.remove(handler)
        return self

    def once(self, event: str, handler: EventHandler) -> WsClient:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            self.off(event, wrapper)
            return handler(*args, **kwargs)

        return self.on(event, wrapper)

    def _emit(self, event: str, *args: Any) -> bool:
        handlers = self._listeners.get(event)
        if not handlers:
            return False
        for handler in list(handlers):
            handler(*args)
        return True

    def remove_all_listeners(self, event: str | None = None) -> WsClient:
        if event:
            self._listeners.pop(event, None)
        else:
            self._listeners.clear()
        return self

    # --- Properties ---

    @property
    def last_pong_at(self) -> float:
        return self._last_pong_at

    @property
    def is_connected(self) -> bool:
        return self._ws is not None and self._ws.state.name == "OPEN"

    @property
    def is_authenticated(self) -> bool:
        return self._authenticated

    # --- Connection ---

    async def connect(self) -> None:
        self._intentional_close = False
        logger.info("Connecting to %s", self._ws_url)

        self._ws = await websockets.asyncio.client.connect(
            self._ws_url,
            ping_interval=self._heartbeat_interval if self._heartbeat_interval > 0 else None,
            ping_timeout=self._heartbeat_timeout if self._heartbeat_timeout > 0 else None,
        )

        self._reconnect_attempts = 0
        logger.info("WebSocket connected")
        self._emit("open")

        await self._authenticate()
        self._receive_task = asyncio.create_task(self._receive_loop())

    async def _authenticate(self) -> None:
        auth_msg = {
            "id": generate_uuid(),
            "operation": "Authenticate",
            "data": {
                "userKey": self._user_key,
                "apiKey": self._api_key,
            },
        }

        auth_event = asyncio.Event()
        auth_error: list[str] = []

        def on_auth_ok() -> None:
            auth_event.set()

        def on_auth_err(err: Exception) -> None:
            if "auth failed" in str(err).lower():
                auth_error.append(str(err))
                auth_event.set()

        self.once("authenticated", on_auth_ok)

        await self._send(auth_msg)

        try:
            # Wait for auth response from the receive loop
            await asyncio.wait_for(auth_event.wait(), timeout=self._auth_timeout)
        except TimeoutError as exc:
            raise EToroAuthError("WebSocket authentication timed out") from exc

        if auth_error:
            raise EToroAuthError(auth_error[0])

        logger.info("WebSocket authenticated")

    # --- Subscribe/Unsubscribe ---

    def subscribe(self, topics: list[str], snapshot: bool = False) -> None:
        self._subscriptions.add(topics)
        msg = {
            "id": generate_uuid(),
            "operation": "Subscribe",
            "data": {"topics": topics, "snapshot": snapshot},
        }
        logger.debug("Subscribing to: %s", ", ".join(topics))
        asyncio.ensure_future(self._send(msg))

    def unsubscribe(self, topics: list[str]) -> None:
        self._subscriptions.remove(topics)
        msg = {
            "id": generate_uuid(),
            "operation": "Unsubscribe",
            "data": {"topics": topics},
        }
        logger.debug("Unsubscribing from: %s", ", ".join(topics))
        asyncio.ensure_future(self._send(msg))

    # --- Disconnect ---

    async def disconnect(self) -> None:
        self._intentional_close = True
        if self._receive_task and not self._receive_task.done():
            self._receive_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._receive_task
            self._receive_task = None
        if self._ws:
            await self._ws.close(1000, "Client disconnect")
            self._ws = None
        self._authenticated = False
        self._subscriptions.clear()

    # --- Internals ---

    async def _receive_loop(self) -> None:
        assert self._ws is not None
        try:
            async for raw in self._ws:
                self._handle_message(str(raw))
        except websockets.ConnectionClosed as exc:
            logger.info("WebSocket closed: %d %s", exc.code, exc.reason)
            self._authenticated = False
            self._emit("close", exc.code, exc.reason)
            if not self._intentional_close:
                await self._attempt_reconnect()
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            logger.error("WebSocket error: %s", exc)
            self._emit("error", exc)

    def _handle_message(self, data: str) -> None:
        try:
            raw = json.loads(data)

            # Auth response
            if raw.get("operation") == "Authenticate" or raw.get("type") == "Authenticate":
                if raw.get("errorCode"):
                    self._emit("error", EToroAuthError(f"WS auth failed: {raw['errorCode']}"))
                    return
                self._authenticated = True
                self._emit("authenticated")
                return

            # Data messages
            if raw.get("messages") and isinstance(raw["messages"], list):
                envelope = WsEnvelope.model_validate(raw)
                self._emit("message", envelope)

                parsed = parse_messages(envelope)
                for msg in parsed:
                    if msg.type == "instrument:rate":
                        self._emit("instrument:rate", msg.data.instrument_id, msg.data.rate)
                    elif msg.type == "private:event":
                        self._emit("private:event", msg.data.event)
        except Exception:
            logger.error("Failed to parse WebSocket message: %s", data[:200])

    async def _attempt_reconnect(self) -> None:
        if self._reconnect_attempts >= self._max_reconnect_attempts:
            logger.error("Max reconnect attempts (%d) reached", self._max_reconnect_attempts)
            self._emit("error", EToroWebSocketError("Max reconnect attempts reached"))
            return

        delay = self._reconnect_delay * (2**self._reconnect_attempts)
        self._reconnect_attempts += 1

        logger.info(
            "Reconnecting in %.1fs (attempt %d/%d)",
            delay,
            self._reconnect_attempts,
            self._max_reconnect_attempts,
        )

        await asyncio.sleep(delay)

        try:
            await self.connect()
            topics = self._subscriptions.get_all()
            if topics:
                logger.info("Re-subscribing to %d topics", len(topics))
                self.subscribe(topics)
        except Exception as exc:
            logger.error("Reconnection failed: %s", exc)

    async def _send(self, msg: Any) -> None:
        if not self._ws:
            raise EToroWebSocketError("WebSocket not connected")
        await self._ws.send(json.dumps(msg))

from __future__ import annotations

import asyncio
import contextlib
import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from ..config.settings import EToroConfig
from ..errors.exceptions import EToroError, EToroValidationError
from ..models.common import TokenResponse
from ..models.enums import CandleDirection, CandleInterval, OrderStatusId
from ..models.market_data import CandlesResponse, InstrumentRate
from ..models.trading import (
    ClosePositionRequest,
    LimitOrderRequest,
    MarketOrderByAmountRequest,
    MarketOrderByUnitsRequest,
    OrderForCloseResponse,
    OrderForOpenInfoResponse,
    OrderForOpenResponse,
    PendingOrder,
    PnlResponse,
    PortfolioResponse,
    Position,
    TradeHistoryEntry,
)
from ..models.websocket import WsInstrumentRate, WsPrivateEvent
from ..rest.rest_client import RestClient
from ..ws.client import WsClient, WsClientOptions
from .instrument_resolver import InstrumentInfo, InstrumentResolver

logger = logging.getLogger("etoropy")

EventHandler = Callable[..., Any]


@dataclass
class OrderOptions:
    """Optional parameters for market and limit orders.

    :param leverage: Leverage multiplier (1 = no leverage).
    :param stop_loss: Stop-loss rate (absolute price level).
    :param take_profit: Take-profit rate (absolute price level).
    :param trailing_stop_loss: Enable trailing stop-loss.
    """

    leverage: int = 1
    stop_loss: float | None = None
    take_profit: float | None = None
    trailing_stop_loss: bool | None = None


class EToroTrading:
    """High-level async client for the eToro Public API.

    Wraps REST endpoints, WebSocket streaming, and instrument resolution
    behind a single entry point.  Supports both ``"demo"`` and ``"real"``
    trading modes (set via :attr:`EToroConfig.mode`).

    Use as an async context manager for automatic cleanup::

        async with EToroTrading() as etoro:
            etoro.resolver.load_bundled_csv()
            await etoro.connect()
            rates = await etoro.get_rates(["AAPL"])
            ...
        # WebSocket closed, HTTP client released

    Events (register with ``etoro.on(event, handler)``)::

        "price"          -> (symbol, instrument_id, WsInstrumentRate)
        "order:update"   -> (WsPrivateEvent)
        "connected"      -> ()
        "disconnected"   -> ()
        "error"          -> (Exception)
        "ws:message"     -> (WsEnvelope)

    :param config: SDK configuration. When *None*, settings are read from
        ``ETORO_``-prefixed environment variables.
    :param kwargs: Forwarded to :class:`EToroConfig` when *config* is *None*.
    """

    def __init__(self, config: EToroConfig | None = None, **kwargs: Any) -> None:
        if config is None:
            config = EToroConfig(**kwargs) if kwargs else EToroConfig()
        self._config = config

        self.rest = RestClient(config)
        self.ws = WsClient(
            WsClientOptions(
                api_key=config.api_key,
                user_key=config.user_key,
                ws_url=config.ws_url,
            )
        )
        self.resolver = InstrumentResolver(self.rest.market_data)

        self._listeners: dict[str, list[EventHandler]] = {}

        self.ws.on("instrument:rate", self._on_instrument_rate)
        self.ws.on("private:event", self._on_private_event)
        self.ws.on("error", lambda err: self._emit("error", err))
        self.ws.on("message", lambda envelope: self._emit("ws:message", envelope))

    def on(self, event: str, handler: EventHandler) -> EToroTrading:
        """Register *handler* for *event*."""
        self._listeners.setdefault(event, []).append(handler)
        return self

    def off(self, event: str, handler: EventHandler) -> EToroTrading:
        """Unregister *handler* from *event*."""
        handlers = self._listeners.get(event)
        if handlers and handler in handlers:
            handlers.remove(handler)
        return self

    def once(self, event: str, handler: EventHandler) -> EToroTrading:
        """Register *handler* for *event*, then auto-unregister after the first call."""

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

    def remove_all_listeners(self, event: str | None = None) -> EToroTrading:
        """Remove all listeners, or only those for *event* if given."""
        if event:
            self._listeners.pop(event, None)
        else:
            self._listeners.clear()
        return self

    def _on_instrument_rate(self, instrument_id: int, rate: WsInstrumentRate) -> None:
        symbol = self.resolver.get_symbol(instrument_id) or str(instrument_id)
        self._emit("price", symbol, instrument_id, rate)

    def _on_private_event(self, event: WsPrivateEvent) -> None:
        self._emit("order:update", event)

    async def connect(self) -> None:
        """Open the WebSocket connection and authenticate.

        Must be called before :meth:`stream_prices` or :meth:`wait_for_order`.
        Emits the ``"connected"`` event on success.
        """
        await self.ws.connect()
        self._emit("connected")

    async def disconnect(self) -> None:
        """Close the WebSocket and release the HTTP client.

        Emits the ``"disconnected"`` event.  Called automatically when
        exiting the ``async with`` block.
        """
        await self.ws.disconnect()
        await self.rest.aclose()
        self._emit("disconnected")

    async def buy_by_amount(
        self,
        symbol_or_id: str | int,
        amount: float,
        options: OrderOptions | None = None,
    ) -> OrderForOpenResponse:
        """Open a long (buy) market order for a dollar *amount*.

        :param symbol_or_id: Instrument symbol (``"AAPL"``) or numeric ID.
        :param amount: Dollar amount to invest.
        :param options: Optional leverage, stop-loss, and take-profit settings.
        :returns: The order response including the assigned order ID.
        """
        opts = options or OrderOptions()
        instrument_id = await self.resolver.resolve(symbol_or_id)
        return await self.rest.execution.open_market_order_by_amount(
            MarketOrderByAmountRequest(
                InstrumentID=instrument_id,
                IsBuy=True,
                Leverage=opts.leverage,
                Amount=amount,
                StopLossRate=opts.stop_loss,
                TakeProfitRate=opts.take_profit,
                IsTslEnabled=opts.trailing_stop_loss,
            )
        )

    async def buy_by_units(
        self,
        symbol_or_id: str | int,
        units: float,
        options: OrderOptions | None = None,
    ) -> OrderForOpenResponse:
        """Open a long (buy) market order for a number of *units*.

        :param symbol_or_id: Instrument symbol or numeric ID.
        :param units: Number of units to buy.
        :param options: Optional leverage, stop-loss, and take-profit settings.
        :returns: The order response including the assigned order ID.
        """
        opts = options or OrderOptions()
        instrument_id = await self.resolver.resolve(symbol_or_id)
        return await self.rest.execution.open_market_order_by_units(
            MarketOrderByUnitsRequest(
                InstrumentID=instrument_id,
                IsBuy=True,
                Leverage=opts.leverage,
                AmountInUnits=units,
                StopLossRate=opts.stop_loss,
                TakeProfitRate=opts.take_profit,
                IsTslEnabled=opts.trailing_stop_loss,
            )
        )

    async def sell_by_amount(
        self,
        symbol_or_id: str | int,
        amount: float,
        options: OrderOptions | None = None,
    ) -> OrderForOpenResponse:
        """Open a short (sell) market order for a dollar *amount*.

        :param symbol_or_id: Instrument symbol or numeric ID.
        :param amount: Dollar amount to invest.
        :param options: Optional leverage, stop-loss, and take-profit settings.
        :returns: The order response including the assigned order ID.
        """
        opts = options or OrderOptions()
        instrument_id = await self.resolver.resolve(symbol_or_id)
        return await self.rest.execution.open_market_order_by_amount(
            MarketOrderByAmountRequest(
                InstrumentID=instrument_id,
                IsBuy=False,
                Leverage=opts.leverage,
                Amount=amount,
                StopLossRate=opts.stop_loss,
                TakeProfitRate=opts.take_profit,
                IsTslEnabled=opts.trailing_stop_loss,
            )
        )

    async def sell_by_units(
        self,
        symbol_or_id: str | int,
        units: float,
        options: OrderOptions | None = None,
    ) -> OrderForOpenResponse:
        """Open a short (sell) market order for a number of *units*.

        :param symbol_or_id: Instrument symbol or numeric ID.
        :param units: Number of units to sell.
        :param options: Optional leverage, stop-loss, and take-profit settings.
        :returns: The order response including the assigned order ID.
        """
        opts = options or OrderOptions()
        instrument_id = await self.resolver.resolve(symbol_or_id)
        return await self.rest.execution.open_market_order_by_units(
            MarketOrderByUnitsRequest(
                InstrumentID=instrument_id,
                IsBuy=False,
                Leverage=opts.leverage,
                AmountInUnits=units,
                StopLossRate=opts.stop_loss,
                TakeProfitRate=opts.take_profit,
                IsTslEnabled=opts.trailing_stop_loss,
            )
        )

    async def close_position(self, position_id: int, units_to_deduct: float | None = None) -> OrderForCloseResponse:
        """Close an open position.

        :param position_id: The position to close.
        :param units_to_deduct: If given, perform a partial close.
        :raises EToroValidationError: If *position_id* is not found in the portfolio.
        """
        portfolio = await self.get_portfolio()
        all_positions = list(portfolio.client_portfolio.positions)
        for mirror in portfolio.client_portfolio.mirrors:
            all_positions.extend(mirror.positions)
        position = next((p for p in all_positions if p.position_id == position_id), None)
        if not position:
            raise EToroValidationError(f"Position {position_id} not found in portfolio", field="position_id")
        return await self.rest.execution.close_position(
            position_id,
            ClosePositionRequest(InstrumentId=position.instrument_id, UnitsToDeduct=units_to_deduct),
        )

    async def close_all_positions(self) -> list[OrderForCloseResponse]:
        """Close all open positions in the portfolio (runs in parallel)."""
        portfolio = await self.get_portfolio()
        return list(
            await asyncio.gather(
                *(
                    self.rest.execution.close_position(
                        p.position_id,
                        ClosePositionRequest(InstrumentId=p.instrument_id),
                    )
                    for p in portfolio.client_portfolio.positions
                )
            )
        )

    async def place_limit_order(
        self,
        symbol_or_id: str | int,
        is_buy: bool,
        trigger_rate: float,
        amount: float,
        options: OrderOptions | None = None,
    ) -> TokenResponse:
        """Place a limit order that triggers at *trigger_rate*.

        :param symbol_or_id: Instrument symbol or numeric ID.
        :param is_buy: ``True`` for buy, ``False`` for sell.
        :param trigger_rate: Price at which the order triggers.
        :param amount: Dollar amount to invest.
        :param options: Optional leverage, stop-loss, and take-profit settings.
        """
        opts = options or OrderOptions()
        instrument_id = await self.resolver.resolve(symbol_or_id)
        return await self.rest.execution.open_limit_order(
            LimitOrderRequest(
                InstrumentID=instrument_id,
                IsBuy=is_buy,
                Leverage=opts.leverage,
                Amount=amount,
                Rate=trigger_rate,
                StopLossRate=opts.stop_loss or 0.0,
                TakeProfitRate=opts.take_profit or 0.0,
                IsTslEnabled=opts.trailing_stop_loss,
            )
        )

    async def cancel_order(self, order_id: int) -> TokenResponse:
        """Cancel a pending market order."""
        return await self.rest.execution.cancel_market_open_order(order_id)

    async def cancel_limit_order(self, order_id: int) -> TokenResponse:
        """Cancel a pending limit order."""
        return await self.rest.execution.cancel_limit_order(order_id)

    async def cancel_all_orders(self) -> list[TokenResponse]:
        """Cancel all pending market orders (runs in parallel)."""
        portfolio = await self.get_portfolio()
        orders = portfolio.client_portfolio.orders_for_open
        return list(await asyncio.gather(*(self.rest.execution.cancel_market_open_order(o.order_id) for o in orders)))

    async def cancel_all_limit_orders(self) -> list[TokenResponse]:
        """Cancel all pending limit orders (runs in parallel)."""
        portfolio = await self.get_portfolio()
        orders = portfolio.client_portfolio.orders
        return list(await asyncio.gather(*(self.rest.execution.cancel_limit_order(o.order_id) for o in orders)))

    async def get_portfolio(self) -> PortfolioResponse:
        """Fetch the full portfolio (positions, mirrors, pending orders)."""
        return await self.rest.info.get_portfolio()

    async def get_positions(self) -> list[Position]:
        """Fetch all open positions."""
        portfolio = await self.get_portfolio()
        return portfolio.client_portfolio.positions

    async def get_pending_orders(self) -> list[PendingOrder]:
        """Fetch all pending orders (limit orders and orders-for-open)."""
        portfolio = await self.get_portfolio()
        return [*portfolio.client_portfolio.orders, *portfolio.client_portfolio.orders_for_open]

    async def get_pnl(self) -> PnlResponse:
        """Fetch the current profit & loss summary."""
        return await self.rest.info.get_pnl()

    async def get_trade_history(
        self,
        min_date: str,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[TradeHistoryEntry]:
        """Fetch closed trade history.

        :param min_date: Earliest date to include (``"YYYY-MM-DD"``).
        :param page: Page number (1-based).
        :param page_size: Number of results per page.
        """
        return await self.rest.info.get_trade_history(min_date, page=page, page_size=page_size)

    async def get_rates(self, symbols_or_ids: list[str | int]) -> list[InstrumentRate]:
        """Fetch live bid/ask rates for the given instruments."""
        ids = list(await asyncio.gather(*(self.resolver.resolve(s) for s in symbols_or_ids)))
        response = await self.rest.market_data.get_rates(ids)
        return response.rates

    async def get_candles(
        self,
        symbol_or_id: str | int,
        interval: CandleInterval,
        count: int,
        direction: CandleDirection = CandleDirection.DESC,
    ) -> CandlesResponse:
        """Fetch historical candlestick data.

        :param symbol_or_id: Instrument symbol or numeric ID.
        :param interval: Candle interval (e.g. ``CandleInterval.ONE_DAY``).
        :param count: Number of candles to fetch (max 1000).
        :param direction: Sort direction (``ASC`` or ``DESC``).
        """
        instrument_id = await self.resolver.resolve(symbol_or_id)
        return await self.rest.market_data.get_candles(instrument_id, direction, interval, count)

    async def stream_prices(self, symbols_or_ids: list[str | int], snapshot: bool = True) -> None:
        """Subscribe to real-time price updates for the given instruments.

        Price ticks are emitted as ``"price"`` events with
        ``(symbol, instrument_id, WsInstrumentRate)`` arguments.
        Requires a prior call to :meth:`connect`.

        :param symbols_or_ids: Instruments to stream.
        :param snapshot: If ``True``, request an initial snapshot on subscribe.
        """
        ids = list(await asyncio.gather(*(self.resolver.resolve(s) for s in symbols_or_ids)))
        topics = [f"instrument:{id_}" for id_ in ids]
        self.ws.subscribe(topics, snapshot)

    async def stop_streaming_prices(self, symbols_or_ids: list[str | int]) -> None:
        """Unsubscribe from price updates for the given instruments."""
        topics: list[str] = []
        for s in symbols_or_ids:
            id_ = s if isinstance(s, int) else self.resolver.get_cached_id(s)
            if id_ is not None:
                topics.append(f"instrument:{id_}")
        if topics:
            self.ws.unsubscribe(topics)

    def subscribe_to_private_events(self) -> None:
        """Subscribe to private account events (order fills, cancellations, etc.)."""
        self.ws.subscribe(["private"])

    def unsubscribe_from_private_events(self) -> None:
        """Unsubscribe from private account events."""
        self.ws.unsubscribe(["private"])

    async def wait_for_order(self, order_id: int, timeout_s: float = 30.0) -> WsPrivateEvent:
        """Block until an order reaches a terminal state.

        Uses a hybrid approach: listens for WebSocket private events
        and, after a 3-second grace period, starts polling the REST
        ``GET /orders/{id}`` endpoint as a fallback.

        :param order_id: The order ID to monitor.
        :param timeout_s: Maximum wait time in seconds.
        :returns: The :class:`WsPrivateEvent` describing the terminal state.
        :raises EToroError: If the order fails, is cancelled, or times out.
        """
        if not self.ws.is_connected:
            raise EToroError("WebSocket not connected -- call connect() before wait_for_order()")

        self.subscribe_to_private_events()

        event_future: asyncio.Future[WsPrivateEvent] = asyncio.get_event_loop().create_future()

        def handler(event: WsPrivateEvent) -> None:
            if event.order_id != order_id:
                return
            if event_future.done():
                return

            if event.status_id == OrderStatusId.EXECUTED:
                event_future.set_result(event)
            elif event.status_id in (OrderStatusId.FAILED, OrderStatusId.CANCELLED):
                status_name = OrderStatusId(event.status_id).name
                reason = event.error_message or event.close_reason or "unknown reason"
                event_future.set_exception(
                    EToroError(f"Order {order_id} {status_name}: {reason} (errorCode: {event.error_code or 'none'})")
                )

        self.on("order:update", handler)

        poll_delay = min(3.0, timeout_s / 2)

        async def _poll_fallback() -> None:
            await asyncio.sleep(poll_delay)
            if event_future.done():
                return
            try:
                info = await self._poll_order_status(order_id, timeout_s - poll_delay)
                if not event_future.done():
                    event_future.set_result(
                        WsPrivateEvent(
                            OrderID=info.order_id,
                            OrderType=info.order_type,
                            StatusID=info.status_id,
                            InstrumentID=info.instrument_id,
                            CID=info.cid,
                            RequestedUnits=info.units,
                            ExecutedUnits=info.units,
                            NetProfit=0,
                            CloseReason="",
                            OpenDateTime=info.request_occurred,
                            RequestOccurred=info.request_occurred,
                            PositionID=info.positions[0].position_id if info.positions else None,
                            Amount=info.amount,
                            ErrorCode=info.error_code,
                            ErrorMessage=info.error_message,
                        )
                    )
            except Exception:
                pass  # WS might still deliver

        poll_task = asyncio.create_task(_poll_fallback())

        try:
            return await asyncio.wait_for(event_future, timeout=timeout_s)
        except TimeoutError as exc:
            raise EToroError(f"Timeout waiting for order {order_id} after {timeout_s}s") from exc
        finally:
            self.off("order:update", handler)
            poll_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await poll_task

    async def _poll_order_status(
        self,
        order_id: int,
        timeout_s: float,
        poll_interval_s: float = 0.5,
    ) -> OrderForOpenInfoResponse:
        elapsed = 0.0
        while elapsed < timeout_s:
            try:
                info = await self.rest.info.get_order(order_id)
                if info.status_id == OrderStatusId.EXECUTED:
                    return info
                if info.status_id in (OrderStatusId.CANCELLED, OrderStatusId.FAILED):
                    status_name = OrderStatusId(info.status_id).name
                    raise EToroError(f"Order {order_id} was {status_name}: {info.error_message or 'unknown reason'}")
            except EToroError:
                raise
            except Exception:
                pass  # 404 etc -- keep polling

            await asyncio.sleep(poll_interval_s)
            elapsed += poll_interval_s

        raise EToroError(f"Timeout waiting for order {order_id} execution after {timeout_s}s")

    async def resolve_instrument(self, symbol_or_id: str | int) -> int:
        """Resolve an instrument symbol to its numeric ID."""
        return await self.resolver.resolve(symbol_or_id)

    async def preload_instruments(self, symbols: list[str]) -> None:
        """Pre-resolve a list of symbols so later lookups are instant."""
        await self.resolver.preload(symbols)

    async def get_display_name(self, symbol_or_id: str | int) -> str:
        """Return the human-readable display name for an instrument."""
        return await self.resolver.get_display_name(symbol_or_id)

    async def get_instrument_info(self, symbol_or_id: str | int) -> InstrumentInfo:
        """Fetch full metadata for an instrument."""
        return await self.resolver.get_instrument_info(symbol_or_id)

    async def get_instrument_info_batch(self, symbols_or_ids: list[str | int]) -> list[InstrumentInfo]:
        """Fetch metadata for multiple instruments in one call."""
        ids = list(await asyncio.gather(*(self.resolver.resolve(s) for s in symbols_or_ids)))
        return await self.resolver.get_instrument_info_batch(ids)

    async def preload_instrument_metadata(self, instrument_ids: list[int]) -> None:
        """Pre-fetch and cache display metadata for the given instrument IDs."""
        await self.resolver.preload_metadata(instrument_ids)

    async def __aenter__(self) -> EToroTrading:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.disconnect()

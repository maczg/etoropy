from __future__ import annotations

from ..config.constants import API_PREFIX
from ..http.client import HttpClient
from ..models.common import TokenResponse
from ..models.enums import TradingMode
from ..models.trading import (
    ClosePositionRequest,
    LimitOrderRequest,
    MarketOrderByAmountRequest,
    MarketOrderByUnitsRequest,
    OrderForCloseResponse,
    OrderForOpenResponse,
)
from ._base import BaseRestClient


class TradingExecutionClient(BaseRestClient):
    """REST client for order execution (open, close, cancel).

    URL routing is mode-aware: demo orders go to
    ``/trading/execution/demo/...``, real orders to ``/trading/execution/...``.
    """

    def __init__(self, http: HttpClient, mode: TradingMode) -> None:
        super().__init__(http)
        self._path_prefix = (
            f"{API_PREFIX}/trading/execution/demo" if mode == "demo" else f"{API_PREFIX}/trading/execution"
        )

    async def open_market_order_by_amount(self, params: MarketOrderByAmountRequest) -> OrderForOpenResponse:
        data = await self._post(f"{self._path_prefix}/market-open-orders/by-amount", params)
        return OrderForOpenResponse.model_validate(data)

    async def open_market_order_by_units(self, params: MarketOrderByUnitsRequest) -> OrderForOpenResponse:
        data = await self._post(f"{self._path_prefix}/market-open-orders/by-units", params)
        return OrderForOpenResponse.model_validate(data)

    async def cancel_market_open_order(self, order_id: int) -> TokenResponse:
        data = await self._delete(f"{self._path_prefix}/market-open-orders/{order_id}")
        return TokenResponse.model_validate(data)

    async def open_limit_order(self, params: LimitOrderRequest) -> TokenResponse:
        data = await self._post(f"{self._path_prefix}/limit-orders", params)
        return TokenResponse.model_validate(data)

    async def cancel_limit_order(self, order_id: int) -> TokenResponse:
        data = await self._delete(f"{self._path_prefix}/limit-orders/{order_id}")
        return TokenResponse.model_validate(data)

    async def close_position(
        self, position_id: int, params: ClosePositionRequest | None = None
    ) -> OrderForCloseResponse:
        body = params if params is not None else {}
        data = await self._post(f"{self._path_prefix}/market-close-orders/positions/{position_id}", body)
        return OrderForCloseResponse.model_validate(data)

    async def cancel_close_order(self, order_id: int) -> TokenResponse:
        data = await self._delete(f"{self._path_prefix}/market-close-orders/{order_id}")
        return TokenResponse.model_validate(data)

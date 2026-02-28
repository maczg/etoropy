from __future__ import annotations

from typing import Any

from ..config.constants import API_PREFIX
from ..http.client import HttpClient
from ..models.enums import TradingMode
from ..models.trading import (
    OrderForOpenInfoResponse,
    PnlResponse,
    PortfolioResponse,
    TradeHistoryEntry,
)
from ._base import BaseRestClient


class TradingInfoClient(BaseRestClient):
    """REST client for trading information (portfolio, PnL, order status, history).

    URL routing is mode-aware with asymmetric paths:
    demo portfolio is at ``/trading/info/demo/portfolio``,
    real portfolio at ``/trading/info/portfolio`` (no ``real`` segment).
    """

    def __init__(self, http: HttpClient, mode: TradingMode) -> None:
        super().__init__(http)
        self._mode = mode
        if mode == "demo":
            self._info_prefix = f"{API_PREFIX}/trading/info/demo"
            self._portfolio_path = f"{API_PREFIX}/trading/info/demo/portfolio"
        else:
            self._info_prefix = f"{API_PREFIX}/trading/info/real"
            self._portfolio_path = f"{API_PREFIX}/trading/info/portfolio"

    async def get_portfolio(self) -> PortfolioResponse:
        data = await self._get(self._portfolio_path)
        return PortfolioResponse.model_validate(data)

    async def get_pnl(self) -> PnlResponse:
        data = await self._get(f"{self._info_prefix}/pnl")
        return PnlResponse.model_validate(data)

    async def get_order(self, order_id: int) -> OrderForOpenInfoResponse:
        data = await self._get(f"{self._info_prefix}/orders/{order_id}")
        return OrderForOpenInfoResponse.model_validate(data)

    async def get_trade_history(
        self,
        min_date: str,
        *,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[TradeHistoryEntry]:
        query: dict[str, Any] = {"minDate": min_date}
        if page is not None:
            query["page"] = page
        if page_size is not None:
            query["pageSize"] = page_size
        # Trade history is only available for real accounts
        if self._mode == "demo":
            return []
        data = await self._get(f"{API_PREFIX}/trading/info/trade/history", query)
        if isinstance(data, list):
            return [TradeHistoryEntry.model_validate(item) for item in data]
        return []

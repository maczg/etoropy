from __future__ import annotations

import pytest

from etoropy.models.trading import (
    ClientPortfolio,
    PnlResponse,
    PortfolioResponse,
    Position,
)
from etoropy.rest.rest_client import RestClient

pytestmark = pytest.mark.integration


class TestGetPortfolio:
    async def test_returns_portfolio(self, rest_client: RestClient) -> None:
        result = await rest_client.info.get_portfolio()
        assert isinstance(result, PortfolioResponse)
        assert isinstance(result.client_portfolio, ClientPortfolio)
        assert result.client_portfolio.credit >= 0.0
        # Positions may be empty on a fresh demo account
        for pos in result.client_portfolio.positions[:5]:
            assert isinstance(pos, Position)
            assert pos.position_id > 0
            assert pos.instrument_id > 0


class TestGetPnl:
    async def test_returns_pnl(self, rest_client: RestClient) -> None:
        result = await rest_client.info.get_pnl()
        assert isinstance(result, PnlResponse)
        assert isinstance(result.client_portfolio, ClientPortfolio)


class TestGetTradeHistory:
    async def test_returns_history(self, rest_client: RestClient) -> None:
        # Trade history is only available for real accounts; demo returns []
        result = await rest_client.info.get_trade_history("2020-01-01", page_size=5)
        assert isinstance(result, list)

    async def test_history_pagination(self, rest_client: RestClient) -> None:
        result = await rest_client.info.get_trade_history("2020-01-01", page=1, page_size=2)
        assert isinstance(result, list)

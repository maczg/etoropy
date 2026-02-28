from __future__ import annotations

import pytest

from etoropy.models.enums import CandleDirection, CandleInterval
from etoropy.models.market_data import (
    Candle,
    CandleGroup,
    CandlesResponse,
    InstrumentRate,
)
from etoropy.models.trading import (
    ClientPortfolio,
    PnlResponse,
    PortfolioResponse,
    Position,
)
from etoropy.trading.client import EToroTrading
from etoropy.trading.instrument_resolver import InstrumentInfo

from .conftest import AAPL_ID, BTC_ID, MSFT_ID, TSLA_ID

pytestmark = pytest.mark.integration


class TestResolveInstrument:
    async def test_resolve_by_symbol(self, etoro: EToroTrading) -> None:
        instrument_id = await etoro.resolve_instrument("AAPL")
        assert instrument_id == AAPL_ID

    async def test_resolve_by_id(self, etoro: EToroTrading) -> None:
        instrument_id = await etoro.resolve_instrument(AAPL_ID)
        assert instrument_id == AAPL_ID

    async def test_resolve_crypto(self, etoro: EToroTrading) -> None:
        instrument_id = await etoro.resolve_instrument("BTC")
        assert instrument_id == BTC_ID


class TestGetDisplayName:
    async def test_returns_name(self, etoro: EToroTrading) -> None:
        name = await etoro.get_display_name("AAPL")
        assert isinstance(name, str)
        assert name != ""


class TestGetInstrumentInfo:
    async def test_single_info(self, etoro: EToroTrading) -> None:
        info = await etoro.get_instrument_info("AAPL")
        assert isinstance(info, InstrumentInfo)
        assert info.instrument_id == AAPL_ID
        assert info.display_name != ""
        assert info.symbol_full == "AAPL"

    async def test_batch_info(self, etoro: EToroTrading) -> None:
        infos = await etoro.get_instrument_info_batch(["AAPL", "TSLA"])
        assert isinstance(infos, list)
        assert len(infos) == 2
        ids = {i.instrument_id for i in infos}
        assert AAPL_ID in ids
        assert TSLA_ID in ids
        for info in infos:
            assert isinstance(info, InstrumentInfo)
            assert info.display_name != ""


class TestGetRates:
    async def test_single_symbol(self, etoro: EToroTrading) -> None:
        rates = await etoro.get_rates(["AAPL"])
        assert len(rates) == 1
        rate = rates[0]
        assert isinstance(rate, InstrumentRate)
        assert rate.instrument_id == AAPL_ID
        assert rate.bid > 0
        assert rate.ask > 0
        assert rate.bid <= rate.ask

    async def test_multiple_symbols(self, etoro: EToroTrading) -> None:
        rates = await etoro.get_rates(["AAPL", "MSFT"])
        assert len(rates) == 2
        ids = {r.instrument_id for r in rates}
        assert ids == {AAPL_ID, MSFT_ID}
        for rate in rates:
            assert rate.bid > 0
            assert rate.ask > 0


class TestGetCandles:
    async def test_daily_candles(self, etoro: EToroTrading) -> None:
        result = await etoro.get_candles("AAPL", CandleInterval.ONE_DAY, 10)
        assert isinstance(result, CandlesResponse)
        assert len(result.candles) > 0
        group = result.candles[0]
        assert isinstance(group, CandleGroup)
        assert group.instrument_id == AAPL_ID
        assert len(group.candles) > 0
        for candle in group.candles:
            assert isinstance(candle, Candle)
            assert candle.high >= candle.low
            assert candle.open > 0
            assert candle.close > 0

    async def test_hourly_candles_asc(self, etoro: EToroTrading) -> None:
        result = await etoro.get_candles(
            "AAPL",
            CandleInterval.ONE_HOUR,
            5,
            direction=CandleDirection.ASC,
        )
        assert isinstance(result, CandlesResponse)
        assert len(result.candles) > 0


class TestGetPortfolio:
    async def test_returns_portfolio(self, etoro: EToroTrading) -> None:
        result = await etoro.get_portfolio()
        assert isinstance(result, PortfolioResponse)
        assert isinstance(result.client_portfolio, ClientPortfolio)
        assert result.client_portfolio.credit >= 0.0

    async def test_get_positions(self, etoro: EToroTrading) -> None:
        positions = await etoro.get_positions()
        assert isinstance(positions, list)
        for pos in positions[:5]:
            assert isinstance(pos, Position)
            assert pos.position_id > 0
            assert pos.instrument_id > 0


class TestGetPnl:
    async def test_returns_pnl(self, etoro: EToroTrading) -> None:
        result = await etoro.get_pnl()
        assert isinstance(result, PnlResponse)
        assert isinstance(result.client_portfolio, ClientPortfolio)


class TestGetTradeHistory:
    async def test_returns_history(self, etoro: EToroTrading) -> None:
        # Trade history is only available for real accounts; demo returns []
        result = await etoro.get_trade_history("2020-01-01", page_size=5)
        assert isinstance(result, list)

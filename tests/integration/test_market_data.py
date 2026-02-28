from __future__ import annotations

import pytest

from etoropy.models.enums import CandleDirection, CandleInterval
from etoropy.models.market_data import (
    Candle,
    CandleGroup,
    CandlesResponse,
    ClosingPrice,
    ClosingPricesResponse,
    Exchange,
    ExchangesResponse,
    InstrumentDisplayData,
    InstrumentRate,
    InstrumentSearchItem,
    InstrumentSearchResponse,
    InstrumentsResponse,
    InstrumentType,
    InstrumentTypesResponse,
    LiveRatesResponse,
    StocksIndustriesResponse,
    StocksIndustry,
)
from etoropy.rest.rest_client import RestClient

from .conftest import AAPL_ID, MSFT_ID, TSLA_ID

pytestmark = pytest.mark.integration


class TestSearchInstruments:
    async def test_search_by_text(self, rest_client: RestClient) -> None:
        result = await rest_client.market_data.search_instruments(
            fields="instrumentId,symbol,displayname",
            search_text="Apple",
            page_size=5,
        )
        assert isinstance(result, InstrumentSearchResponse)
        assert len(result.items) > 0
        first = result.items[0]
        assert isinstance(first, InstrumentSearchItem)
        assert first.instrument_id != 0

    async def test_search_by_symbol(self, rest_client: RestClient) -> None:
        result = await rest_client.market_data.search_instruments(
            fields="instrumentId,symbol,displayname",
            internal_symbol_full="AAPL",
        )
        assert isinstance(result, InstrumentSearchResponse)
        assert len(result.items) > 0
        assert any(item.instrument_id == AAPL_ID for item in result.items)


class TestGetInstruments:
    async def test_single_instrument(self, rest_client: RestClient) -> None:
        result = await rest_client.market_data.get_instruments(instrument_ids=[AAPL_ID])
        assert isinstance(result, InstrumentsResponse)
        assert len(result.instrument_display_datas) == 1
        inst = result.instrument_display_datas[0]
        assert isinstance(inst, InstrumentDisplayData)
        assert inst.instrument_id == AAPL_ID
        assert inst.symbol_full == "AAPL"
        assert inst.instrument_display_name != ""

    async def test_multiple_instruments(self, rest_client: RestClient) -> None:
        result = await rest_client.market_data.get_instruments(instrument_ids=[AAPL_ID, TSLA_ID])
        assert isinstance(result, InstrumentsResponse)
        assert len(result.instrument_display_datas) == 2
        returned_ids = {d.instrument_id for d in result.instrument_display_datas}
        assert returned_ids == {AAPL_ID, TSLA_ID}


class TestGetRates:
    async def test_single_rate(self, rest_client: RestClient) -> None:
        result = await rest_client.market_data.get_rates([AAPL_ID])
        assert isinstance(result, LiveRatesResponse)
        assert len(result.rates) == 1
        rate = result.rates[0]
        assert isinstance(rate, InstrumentRate)
        assert rate.instrument_id == AAPL_ID
        assert rate.bid > 0
        assert rate.ask > 0
        assert rate.bid <= rate.ask

    async def test_multiple_rates(self, rest_client: RestClient) -> None:
        result = await rest_client.market_data.get_rates([AAPL_ID, MSFT_ID])
        assert isinstance(result, LiveRatesResponse)
        assert len(result.rates) == 2
        for rate in result.rates:
            assert isinstance(rate, InstrumentRate)
            assert rate.bid > 0
            assert rate.ask > 0


class TestGetCandles:
    async def test_daily_candles(self, rest_client: RestClient) -> None:
        result = await rest_client.market_data.get_candles(
            instrument_id=AAPL_ID,
            direction=CandleDirection.DESC,
            interval=CandleInterval.ONE_DAY,
            candles_count=5,
        )
        assert isinstance(result, CandlesResponse)
        assert len(result.candles) > 0
        group = result.candles[0]
        assert isinstance(group, CandleGroup)
        assert group.instrument_id == AAPL_ID
        assert len(group.candles) > 0
        candle = group.candles[0]
        assert isinstance(candle, Candle)
        assert candle.high >= candle.low
        assert candle.open > 0
        assert candle.close > 0


class TestGetInstrumentTypes:
    async def test_returns_types(self, rest_client: RestClient) -> None:
        result = await rest_client.market_data.get_instrument_types()
        assert isinstance(result, InstrumentTypesResponse)
        assert len(result.instrument_types) > 0
        first = result.instrument_types[0]
        assert isinstance(first, InstrumentType)
        assert first.instrument_type_id > 0
        assert first.instrument_type_description != ""


class TestGetClosingPrices:
    async def test_returns_prices(self, rest_client: RestClient) -> None:
        result = await rest_client.market_data.get_closing_prices()
        assert isinstance(result, ClosingPricesResponse)
        assert len(result.closing_prices) > 0
        price = result.closing_prices[0]
        assert isinstance(price, ClosingPrice)
        assert price.instrument_id > 0
        assert price.official_closing_price > 0


class TestGetStocksIndustries:
    async def test_returns_industries(self, rest_client: RestClient) -> None:
        result = await rest_client.market_data.get_stocks_industries()
        assert isinstance(result, StocksIndustriesResponse)
        assert len(result.stocks_industries) > 0
        industry = result.stocks_industries[0]
        assert isinstance(industry, StocksIndustry)
        assert industry.stocks_industry_id > 0


class TestGetExchanges:
    async def test_returns_exchanges(self, rest_client: RestClient) -> None:
        result = await rest_client.market_data.get_exchanges()
        assert isinstance(result, ExchangesResponse)
        assert len(result.exchange_info) > 0
        exchange = result.exchange_info[0]
        assert isinstance(exchange, Exchange)
        assert exchange.exchange_id > 0
        assert exchange.exchange_description != ""

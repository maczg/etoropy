from __future__ import annotations

import asyncio
from typing import Any

from ..config.constants import API_PREFIX, MAX_CANDLES, MAX_RATE_INSTRUMENT_IDS
from ..errors.exceptions import EToroValidationError
from ..models.enums import CandleDirection, CandleInterval
from ..models.market_data import (
    CandlesResponse,
    ClosingPricesResponse,
    ExchangesResponse,
    InstrumentSearchResponse,
    InstrumentsResponse,
    InstrumentTypesResponse,
    LiveRatesResponse,
    StocksIndustriesResponse,
)
from ._base import BaseRestClient


class MarketDataClient(BaseRestClient):
    """REST client for market data endpoints (instruments, rates, candles, exchanges).

    Note: the ``get_rates()`` and ``get_instruments()`` methods fan out
    one request per instrument ID using ``asyncio.gather()``, because the
    eToro API returns 500 when multiple IDs are comma-separated.
    """
    async def search_instruments(
        self,
        fields: str,
        *,
        search_text: str | None = None,
        internal_symbol_full: str | None = None,
        page_size: int | None = None,
        page_number: int | None = None,
        sort: str | None = None,
    ) -> InstrumentSearchResponse:
        query: dict[str, Any] = {"fields": fields}
        if search_text is not None:
            query["searchText"] = search_text
        if internal_symbol_full is not None:
            query["internalSymbolFull"] = internal_symbol_full
        if page_size is not None:
            query["pageSize"] = page_size
        if page_number is not None:
            query["pageNumber"] = page_number
        if sort is not None:
            query["sort"] = sort

        data = await self._get(f"{API_PREFIX}/market-data/search", query)
        return InstrumentSearchResponse.model_validate(data)

    async def get_instruments(
        self,
        *,
        instrument_ids: list[int] | None = None,
        exchange_ids: list[int] | None = None,
        stocks_industry_ids: list[int] | None = None,
        instrument_type_ids: list[int] | None = None,
    ) -> InstrumentsResponse:
        if instrument_ids and len(instrument_ids) > 1:
            results = await asyncio.gather(
                *(
                    self._get(
                        f"{API_PREFIX}/market-data/instruments",
                        {
                            "instrumentIds": str(id_),
                            "exchangeIds": ",".join(map(str, exchange_ids)) if exchange_ids else None,
                            "stocksIndustryIds": ",".join(map(str, stocks_industry_ids))
                            if stocks_industry_ids
                            else None,
                            "instrumentTypeIds": ",".join(map(str, instrument_type_ids))
                            if instrument_type_ids
                            else None,
                        },
                    )
                    for id_ in instrument_ids
                )
            )
            all_datas = []
            for r in results:
                resp = InstrumentsResponse.model_validate(r)
                all_datas.extend(resp.instrument_display_datas)
            return InstrumentsResponse(instrumentDisplayDatas=all_datas)

        query: dict[str, Any] = {}
        if instrument_ids and len(instrument_ids) == 1:
            query["instrumentIds"] = str(instrument_ids[0])
        if exchange_ids:
            query["exchangeIds"] = ",".join(map(str, exchange_ids))
        if stocks_industry_ids:
            query["stocksIndustryIds"] = ",".join(map(str, stocks_industry_ids))
        if instrument_type_ids:
            query["instrumentTypeIds"] = ",".join(map(str, instrument_type_ids))

        data = await self._get(f"{API_PREFIX}/market-data/instruments", query or None)
        return InstrumentsResponse.model_validate(data)

    async def get_rates(self, instrument_ids: list[int] | None = None) -> LiveRatesResponse:
        if not instrument_ids:
            data = await self._get(f"{API_PREFIX}/market-data/instruments/rates")
            return LiveRatesResponse.model_validate(data)

        if len(instrument_ids) > MAX_RATE_INSTRUMENT_IDS:
            raise EToroValidationError(
                f"Cannot request more than {MAX_RATE_INSTRUMENT_IDS} instruments at once",
                field="instrument_ids",
            )

        if len(instrument_ids) == 1:
            data = await self._get(
                f"{API_PREFIX}/market-data/instruments/rates",
                {"instrumentIds": str(instrument_ids[0])},
            )
            return LiveRatesResponse.model_validate(data)

        # Fan-out: individual requests per ID (comma-separated causes 500)
        results = await asyncio.gather(
            *(
                self._get(
                    f"{API_PREFIX}/market-data/instruments/rates",
                    {"instrumentIds": str(id_)},
                )
                for id_ in instrument_ids
            )
        )
        all_rates = []
        for r in results:
            resp = LiveRatesResponse.model_validate(r)
            all_rates.extend(resp.rates)
        return LiveRatesResponse(rates=all_rates)

    async def get_candles(
        self,
        instrument_id: int,
        direction: CandleDirection,
        interval: CandleInterval,
        candles_count: int,
    ) -> CandlesResponse:
        if candles_count > MAX_CANDLES:
            raise EToroValidationError(
                f"Cannot request more than {MAX_CANDLES} candles at once",
                field="candles_count",
            )
        data = await self._get(
            f"{API_PREFIX}/market-data/instruments/{instrument_id}/history/candles/{direction}/{interval}/{candles_count}"
        )
        return CandlesResponse.model_validate(data)

    async def get_instrument_types(self) -> InstrumentTypesResponse:
        data = await self._get(f"{API_PREFIX}/market-data/instrument-types")
        return InstrumentTypesResponse.model_validate(data)

    async def get_closing_prices(self) -> ClosingPricesResponse:
        data = await self._get(f"{API_PREFIX}/market-data/instruments/closing-prices")
        return ClosingPricesResponse.model_validate(data)

    async def get_stocks_industries(self) -> StocksIndustriesResponse:
        data = await self._get(f"{API_PREFIX}/market-data/instruments/industries")
        return StocksIndustriesResponse.model_validate(data)

    async def get_exchanges(self) -> ExchangesResponse:
        data = await self._get(f"{API_PREFIX}/market-data/exchanges")
        return ExchangesResponse.model_validate(data)

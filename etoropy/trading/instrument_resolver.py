from __future__ import annotations

import importlib.resources
from dataclasses import dataclass

from ..errors.exceptions import EToroValidationError
from ..models.market_data import InstrumentDisplayData
from ..rest.market_data import MarketDataClient


@dataclass
class InstrumentInfo:
    """Metadata for a resolved instrument (symbol, display name, exchange, etc.)."""

    instrument_id: int
    display_name: str
    symbol_full: str
    instrument_type_id: int
    exchange_id: int
    instrument_type_sub_category_id: int | None = None
    price_source: str = ""
    has_expiration_date: bool = False
    is_internal_instrument: bool = False
    image_url: str | None = None


class InstrumentResolver:
    """Translates human-readable symbols ("AAPL", "BTC") to eToro integer instrument IDs.

    Resolution goes through three tiers, in order:

    1. **In-memory cache** -- populated from the bundled CSV (``load_bundled_csv()``)
       or via ``register()`` / ``register_many()``.  Instant, no network call.
    2. **API exact match** -- queries ``/market-data/search`` with the
       ``internalSymbolFull`` filter.
    3. **API text search** -- free-text fallback on the same endpoint.

    Every successful lookup is cached for the lifetime of the resolver, so
    repeated calls for the same symbol are free.

    Typical usage::

        resolver = InstrumentResolver(market_data_client)
        resolver.load_bundled_csv()          # load 5,200+ symbols
        instrument_id = await resolver.resolve("AAPL")
        info = await resolver.get_instrument_info("AAPL")
    """

    def __init__(self, market_data: MarketDataClient) -> None:
        self._market_data = market_data
        self._symbol_to_id: dict[str, int] = {}
        self._id_to_symbol: dict[int, str] = {}
        self._id_to_info: dict[int, InstrumentInfo] = {}

    def register(self, symbol: str, instrument_id: int) -> None:
        upper = symbol.upper()
        self._symbol_to_id[upper] = instrument_id
        self._id_to_symbol[instrument_id] = upper

    def register_many(self, entries: list[tuple[str, int]]) -> None:
        for symbol, id_ in entries:
            self.register(symbol, id_)

    def load_from_csv(self, csv_content: str) -> int:
        lines = csv_content.split("\n")
        loaded = 0
        for line in lines[1:]:  # skip header
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            try:
                id_ = int(parts[0])
            except (ValueError, IndexError):
                continue
            symbol = (parts[2] if len(parts) > 2 else "").strip()
            if id_ > 0 and symbol:
                self.register(symbol, id_)
                loaded += 1
        return loaded

    def load_bundled_csv(self) -> int:
        ref = importlib.resources.files("etoropy.data").joinpath("instruments.csv")
        csv_content = ref.read_text(encoding="utf-8")
        return self.load_from_csv(csv_content)

    async def resolve(self, symbol_or_id: str | int) -> int:
        if isinstance(symbol_or_id, int):
            return symbol_or_id

        upper = symbol_or_id.upper()
        cached = self._symbol_to_id.get(upper)
        if cached is not None:
            return cached

        # Step 1: Search by exact symbol
        result = await self._market_data.search_instruments(
            fields="instrumentId",
            internal_symbol_full=upper,
            page_size=5,
        )

        valid = [item for item in result.items if item.instrument_id > 0]
        if valid:
            instrument_id = valid[0].instrument_id
            self._symbol_to_id[upper] = instrument_id
            self._id_to_symbol[instrument_id] = upper
            return instrument_id

        # Step 2: Fallback to text search
        text_result = await self._market_data.search_instruments(
            fields="instrumentId",
            search_text=symbol_or_id,
            page_size=10,
        )

        valid_text = [item for item in text_result.items if item.instrument_id > 0]
        if not valid_text:
            raise EToroValidationError(f"Instrument not found: {symbol_or_id}")

        instrument_id = valid_text[0].instrument_id
        self._symbol_to_id[upper] = instrument_id
        self._id_to_symbol[instrument_id] = upper
        return instrument_id

    # --- Metadata / Display Name Lookups ---

    async def get_instrument_info(self, symbol_or_id: str | int) -> InstrumentInfo:
        instrument_id = symbol_or_id if isinstance(symbol_or_id, int) else await self.resolve(symbol_or_id)

        cached = self._id_to_info.get(instrument_id)
        if cached:
            return cached

        await self._fetch_and_cache_metadata([instrument_id])

        info = self._id_to_info.get(instrument_id)
        if not info:
            raise EToroValidationError(
                f"Instrument metadata not found for ID: {instrument_id}",
                field="instrument_id",
            )
        return info

    async def get_instrument_info_batch(self, instrument_ids: list[int]) -> list[InstrumentInfo]:
        uncached = [id_ for id_ in instrument_ids if id_ not in self._id_to_info]
        if uncached:
            await self._fetch_and_cache_metadata(uncached)
        return [self._id_to_info[id_] for id_ in instrument_ids if id_ in self._id_to_info]

    async def get_display_name(self, symbol_or_id: str | int) -> str:
        info = await self.get_instrument_info(symbol_or_id)
        return info.display_name

    async def get_symbol_full(self, symbol_or_id: str | int) -> str:
        info = await self.get_instrument_info(symbol_or_id)
        return info.symbol_full

    def get_cached_display_name(self, instrument_id: int) -> str | None:
        info = self._id_to_info.get(instrument_id)
        return info.display_name if info else None

    def get_cached_info(self, instrument_id: int) -> InstrumentInfo | None:
        return self._id_to_info.get(instrument_id)

    def get_symbol(self, instrument_id: int) -> str | None:
        return self._id_to_symbol.get(instrument_id)

    def get_cached_id(self, symbol: str) -> int | None:
        return self._symbol_to_id.get(symbol.upper())

    async def preload(self, symbols: list[str]) -> None:
        for s in symbols:
            await self.resolve(s)

    async def preload_metadata(self, instrument_ids: list[int]) -> None:
        uncached = [id_ for id_ in instrument_ids if id_ not in self._id_to_info]
        if uncached:
            await self._fetch_and_cache_metadata(uncached)

    def clear_cache(self) -> None:
        self._symbol_to_id.clear()
        self._id_to_symbol.clear()
        self._id_to_info.clear()

    @property
    def size(self) -> int:
        return len(self._symbol_to_id)

    @property
    def metadata_size(self) -> int:
        return len(self._id_to_info)

    # --- Private helpers ---

    async def _fetch_and_cache_metadata(self, instrument_ids: list[int]) -> None:
        metadata = await self._market_data.get_instruments(instrument_ids=instrument_ids)
        for data in metadata.instrument_display_datas:
            self._cache_display_data(data)

    def _cache_display_data(self, data: InstrumentDisplayData) -> None:
        image_url = None
        for img in data.images:
            if img.width == 150:
                image_url = img.uri
                break
        if image_url is None:
            for img in data.images:
                if img.width == 50:
                    image_url = img.uri
                    break

        info = InstrumentInfo(
            instrument_id=data.instrument_id,
            display_name=data.instrument_display_name,
            symbol_full=data.symbol_full,
            instrument_type_id=data.instrument_type_id,
            exchange_id=data.exchange_id,
            instrument_type_sub_category_id=data.instrument_type_sub_category_id,
            price_source=data.price_source,
            has_expiration_date=data.has_expiration_date,
            is_internal_instrument=data.is_internal_instrument,
            image_url=image_url,
        )

        self._id_to_info[data.instrument_id] = info

        if data.symbol_full:
            symbol = data.symbol_full.upper()
            self._symbol_to_id[symbol] = data.instrument_id
            self._id_to_symbol[data.instrument_id] = symbol

from __future__ import annotations

from pydantic import BaseModel, Field


class InstrumentSearchParams(BaseModel):
    fields: str
    search_text: str | None = None
    internal_symbol_full: str | None = None
    page_size: int | None = None
    page_number: int | None = None
    sort: str | None = None


class InstrumentSearchItem(BaseModel):
    model_config = {"extra": "allow"}

    instrument_id: int = Field(alias="instrumentId")
    symbol: str = ""
    displayname: str = ""
    instrument_type_id: int = Field(0, alias="instrumentTypeID")
    exchange_id: int = Field(0, alias="exchangeID")
    is_open: bool = Field(False, alias="isOpen")
    is_currently_tradable: bool = Field(False, alias="isCurrentlyTradable")
    is_buy_enabled: bool = Field(False, alias="isBuyEnabled")
    is_delisted: bool = Field(False, alias="isDelisted")
    is_exchange_open: bool = Field(False, alias="isExchangeOpen")
    current_rate: float = Field(0.0, alias="currentRate")
    daily_price_change: float = Field(0.0, alias="dailyPriceChange")
    abs_daily_price_change: float = Field(0.0, alias="absDailyPriceChange")
    weekly_price_change: float = Field(0.0, alias="weeklyPriceChange")
    monthly_price_change: float = Field(0.0, alias="monthlyPriceChange")
    three_month_price_change: float = Field(0.0, alias="threeMonthPriceChange")
    six_month_price_change: float = Field(0.0, alias="sixMonthPriceChange")
    one_year_price_change: float = Field(0.0, alias="oneYearPriceChange")
    internal_asset_class_id: int = Field(0, alias="internalAssetClassId")
    internal_asset_class_name: str = Field("", alias="internalAssetClassName")
    logo_35x35: str = Field("", alias="logo35x35")
    logo_50x50: str = Field("", alias="logo50x50")
    logo_150x150: str = Field("", alias="logo150x150")


class InstrumentSearchResponse(BaseModel):
    items: list[InstrumentSearchItem] = []
    page: int = 0
    page_size: int = Field(0, alias="pageSize")
    total_items: int = Field(0, alias="totalItems")


class InstrumentImage(BaseModel):
    instrument_id: int = Field(alias="instrumentId")
    width: int
    height: int
    uri: str
    background_color: str = Field("", alias="backgroundColor")
    text_color: str = Field("", alias="textColor")


class InstrumentDisplayData(BaseModel):
    model_config = {"extra": "allow"}

    instrument_id: int = Field(alias="instrumentID")
    instrument_display_name: str = Field(alias="instrumentDisplayName")
    instrument_type_id: int = Field(alias="instrumentTypeID")
    exchange_id: int = Field(alias="exchangeID")
    symbol_full: str = Field(alias="symbolFull")
    instrument_type_sub_category_id: int | None = Field(None, alias="instrumentTypeSubCategoryID")
    price_source: str = Field("", alias="priceSource")
    has_expiration_date: bool = Field(False, alias="hasExpirationDate")
    is_internal_instrument: bool = Field(False, alias="isInternalInstrument")
    images: list[InstrumentImage] = []


class InstrumentsResponse(BaseModel):
    instrument_display_datas: list[InstrumentDisplayData] = Field(
        default_factory=list, alias="instrumentDisplayDatas"
    )


class GetInstrumentsParams(BaseModel):
    instrument_ids: list[int] | None = None
    exchange_ids: list[int] | None = None
    stocks_industry_ids: list[int] | None = None
    instrument_type_ids: list[int] | None = None


class InstrumentRate(BaseModel):
    model_config = {"extra": "allow"}

    instrument_id: int = Field(alias="instrumentID")
    ask: float
    bid: float
    last_execution: float = Field(0.0, alias="lastExecution")
    conversion_rate_ask: float = Field(0.0, alias="conversionRateAsk")
    conversion_rate_bid: float = Field(0.0, alias="conversionRateBid")
    date: str = ""
    unit_margin: float = Field(0.0, alias="unitMargin")
    unit_margin_ask: float = Field(0.0, alias="unitMarginAsk")
    unit_margin_bid: float = Field(0.0, alias="unitMarginBid")
    price_rate_id: int = Field(0, alias="priceRateID")
    bid_discounted: float = Field(0.0, alias="bidDiscounted")
    ask_discounted: float = Field(0.0, alias="askDiscounted")
    unit_margin_bid_discounted: float = Field(0.0, alias="unitMarginBidDiscounted")
    unit_margin_ask_discounted: float = Field(0.0, alias="unitMarginAskDiscounted")


class LiveRatesResponse(BaseModel):
    rates: list[InstrumentRate] = []


class Candle(BaseModel):
    instrument_id: int = Field(alias="instrumentID")
    from_date: str = Field(alias="fromDate")
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


class CandleGroup(BaseModel):
    instrument_id: int = Field(alias="instrumentId")
    candles: list[Candle] = []
    range_open: float = Field(0.0, alias="rangeOpen")
    range_close: float = Field(0.0, alias="rangeClose")
    range_high: float = Field(0.0, alias="rangeHigh")
    range_low: float = Field(0.0, alias="rangeLow")
    volume: float = 0.0


class CandlesResponse(BaseModel):
    interval: str = ""
    candles: list[CandleGroup] = []


class Exchange(BaseModel):
    model_config = {"extra": "allow"}

    exchange_id: int = Field(alias="exchangeID")
    exchange_description: str = Field("", alias="exchangeDescription")


class ExchangesResponse(BaseModel):
    exchange_info: list[Exchange] = Field(default_factory=list, alias="exchangeInfo")


class InstrumentType(BaseModel):
    model_config = {"extra": "allow"}

    instrument_type_id: int = Field(alias="instrumentTypeID")
    instrument_type_description: str = Field("", alias="instrumentTypeDescription")


class InstrumentTypesResponse(BaseModel):
    instrument_types: list[InstrumentType] = Field(default_factory=list, alias="instrumentTypes")


class StocksIndustry(BaseModel):
    model_config = {"extra": "allow"}

    stocks_industry_id: int = Field(alias="stocksIndustryId")
    name: str = ""


class StocksIndustriesResponse(BaseModel):
    stocks_industries: list[StocksIndustry] = Field(default_factory=list, alias="stocksIndustries")


class ClosingPrice(BaseModel):
    model_config = {"extra": "allow"}

    instrument_id: int = Field(alias="instrumentId")
    closing_price: float = Field(alias="closingPrice")


class ClosingPricesResponse(BaseModel):
    closing_prices: list[ClosingPrice] = Field(default_factory=list, alias="closingPrices")

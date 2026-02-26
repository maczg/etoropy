from etoropy.models.market_data import (
    InstrumentRate,
    InstrumentSearchItem,
    InstrumentSearchResponse,
    LiveRatesResponse,
)
from etoropy.models.trading import (
    ClosePositionRequest,
    MarketOrderByAmountRequest,
    OrderForOpen,
    OrderForOpenResponse,
    PendingOrder,
    Position,
)
from etoropy.models.websocket import WsEnvelope, WsInstrumentRate, WsPrivateEvent


def test_instrument_rate_from_api() -> None:
    data = {
        "instrumentID": 1001,
        "ask": 150.25,
        "bid": 150.10,
        "lastExecution": 150.15,
        "conversionRateAsk": 1.0,
        "conversionRateBid": 1.0,
        "date": "2024-01-01T00:00:00Z",
        "unitMargin": 0.5,
        "unitMarginAsk": 0.25,
        "unitMarginBid": 0.25,
        "priceRateID": 12345,
        "bidDiscounted": 150.05,
        "askDiscounted": 150.20,
        "unitMarginBidDiscounted": 0.24,
        "unitMarginAskDiscounted": 0.26,
    }
    rate = InstrumentRate.model_validate(data)
    assert rate.instrument_id == 1001
    assert rate.ask == 150.25
    assert rate.bid == 150.10


def test_instrument_search_response() -> None:
    data = {
        "items": [
            {
                "instrumentId": 1001,
                "symbol": "AAPL",
                "displayname": "Apple",
                "instrumentTypeID": 5,
                "exchangeID": 1,
                "isOpen": True,
                "isCurrentlyTradable": True,
                "isBuyEnabled": True,
                "isDelisted": False,
                "isExchangeOpen": True,
                "currentRate": 150.0,
                "dailyPriceChange": 1.5,
                "absDailyPriceChange": 1.5,
                "weeklyPriceChange": 3.0,
                "monthlyPriceChange": 5.0,
                "threeMonthPriceChange": 10.0,
                "sixMonthPriceChange": 15.0,
                "oneYearPriceChange": 30.0,
                "internalAssetClassId": 1,
                "internalAssetClassName": "Stocks",
                "logo35x35": "",
                "logo50x50": "",
                "logo150x150": "",
            }
        ],
        "page": 1,
        "pageSize": 10,
        "totalItems": 1,
    }
    resp = InstrumentSearchResponse.model_validate(data)
    assert len(resp.items) == 1
    assert resp.items[0].instrument_id == 1001
    assert resp.items[0].symbol == "AAPL"


def test_market_order_request_serialization() -> None:
    req = MarketOrderByAmountRequest(
        InstrumentID=1001,
        IsBuy=True,
        Leverage=1,
        Amount=100.0,
        StopLossRate=140.0,
        TakeProfitRate=160.0,
    )
    data = req.model_dump(by_alias=True, exclude_none=True)
    assert data["InstrumentID"] == 1001
    assert data["IsBuy"] is True
    assert data["Leverage"] == 1
    assert data["Amount"] == 100.0
    assert data["StopLossRate"] == 140.0
    assert data["TakeProfitRate"] == 160.0


def test_close_position_request_serialization() -> None:
    req = ClosePositionRequest(InstrumentId=1001, UnitsToDeduct=5.0)
    data = req.model_dump(by_alias=True, exclude_none=True)
    assert data["InstrumentId"] == 1001
    assert data["UnitsToDeduct"] == 5.0


def test_position_from_api() -> None:
    data = {
        "positionID": 123,
        "CID": 456,
        "openDateTime": "2024-01-01T00:00:00Z",
        "openRate": 150.0,
        "instrumentID": 1001,
        "isBuy": True,
        "leverage": 1,
        "takeProfitRate": 160.0,
        "stopLossRate": 140.0,
        "amount": 100.0,
        "orderID": 789,
        "orderType": 1,
        "units": 0.66,
        "totalFees": 0.0,
    }
    pos = Position.model_validate(data)
    assert pos.position_id == 123
    assert pos.instrument_id == 1001
    assert pos.is_buy is True


def test_pending_order_from_api() -> None:
    data = {
        "orderID": 100,
        "CID": 200,
        "openDateTime": "2024-01-01T00:00:00Z",
        "instrumentID": 1001,
        "isBuy": True,
        "takeProfitRate": 160.0,
        "stopLossRate": 140.0,
        "rate": 150.0,
        "amount": 100.0,
        "leverage": 2,
        "units": 1.0,
    }
    order = PendingOrder.model_validate(data)
    assert order.order_id == 100
    assert order.leverage == 2


def test_order_for_open_response() -> None:
    data = {
        "orderForOpen": {
            "instrumentID": 1001,
            "amount": 100.0,
            "isBuy": True,
            "leverage": 1,
            "stopLossRate": 140.0,
            "takeProfitRate": 160.0,
            "isTslEnabled": False,
            "mirrorID": 0,
            "totalExternalCosts": 0.0,
            "orderID": 555,
            "orderType": 1,
            "statusID": 1,
            "CID": 999,
            "openDateTime": "2024-01-01T00:00:00Z",
            "lastUpdate": "2024-01-01T00:00:01Z",
        },
        "token": "abc123",
    }
    resp = OrderForOpenResponse.model_validate(data)
    assert resp.token == "abc123"
    assert resp.order_for_open.order_id == 555
    assert resp.order_for_open.status_id == 1


def test_ws_instrument_rate() -> None:
    data = {"Ask": 150.25, "Bid": 150.10, "LastExecution": 150.15, "Date": "2024-01-01", "PriceRateID": 12345}
    rate = WsInstrumentRate.model_validate(data)
    assert rate.ask == 150.25
    assert rate.bid == 150.10


def test_ws_private_event() -> None:
    data = {
        "OrderID": 100,
        "OrderType": 1,
        "StatusID": 3,
        "InstrumentID": 1001,
        "CID": 200,
        "RequestedUnits": 1.0,
        "ExecutedUnits": 1.0,
        "NetProfit": 10.0,
        "CloseReason": "",
        "OpenDateTime": "2024-01-01T00:00:00Z",
        "RequestOccurred": "2024-01-01T00:00:00Z",
        "PositionID": 50,
    }
    event = WsPrivateEvent.model_validate(data)
    assert event.order_id == 100
    assert event.status_id == 3
    assert event.position_id == 50


def test_ws_envelope() -> None:
    data = {
        "messages": [
            {
                "topic": "instrument:1001",
                "content": '{"Ask": 150.25, "Bid": 150.10}',
                "id": "msg-1",
                "type": "rate",
            }
        ]
    }
    envelope = WsEnvelope.model_validate(data)
    assert len(envelope.messages) == 1
    assert envelope.messages[0].topic == "instrument:1001"

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

# --- Operations ---


class WsAuthenticateOperation(BaseModel):
    id: str
    operation: str = "Authenticate"
    data: dict[str, str]


class WsSubscribeOperation(BaseModel):
    id: str
    operation: str = "Subscribe"
    data: dict[str, Any]


class WsUnsubscribeOperation(BaseModel):
    id: str
    operation: str = "Unsubscribe"
    data: dict[str, list[str]]


# --- Message Envelope ---


class WsMessage(BaseModel):
    topic: str
    content: str
    id: str
    type: str


class WsEnvelope(BaseModel):
    messages: list[WsMessage] = []


# --- Parsed Event Data ---


class WsInstrumentRate(BaseModel):
    ask: float = Field(alias="Ask")
    bid: float = Field(alias="Bid")
    last_execution: float = Field(0.0, alias="LastExecution")
    date: str = Field("", alias="Date")
    price_rate_id: int = Field(0, alias="PriceRateID")


class WsPrivateEvent(BaseModel):
    model_config = {"extra": "allow"}

    order_id: int = Field(alias="OrderID")
    order_type: int = Field(alias="OrderType")
    status_id: int = Field(alias="StatusID")
    instrument_id: int = Field(alias="InstrumentID")
    cid: int = Field(alias="CID")
    requested_units: float = Field(0.0, alias="RequestedUnits")
    executed_units: float = Field(0.0, alias="ExecutedUnits")
    net_profit: float = Field(0.0, alias="NetProfit")
    close_reason: str = Field("", alias="CloseReason")
    open_date_time: str = Field("", alias="OpenDateTime")
    request_occurred: str = Field("", alias="RequestOccurred")
    error_code: int | None = Field(None, alias="ErrorCode")
    error_message: str | None = Field(None, alias="ErrorMessage")
    position_id: int | None = Field(None, alias="PositionID")
    rate: float | None = Field(None, alias="Rate")
    amount: float | None = Field(None, alias="Amount")
    is_buy: bool | None = Field(None, alias="IsBuy")
    leverage: int | None = Field(None, alias="Leverage")

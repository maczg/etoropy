from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class MarketOrderByAmountRequest(BaseModel):
    instrument_id: int = Field(alias="InstrumentID", serialization_alias="InstrumentID")
    is_buy: bool = Field(alias="IsBuy", serialization_alias="IsBuy")
    leverage: int = Field(alias="Leverage", serialization_alias="Leverage")
    amount: float = Field(alias="Amount", serialization_alias="Amount")
    stop_loss_rate: float | None = Field(None, alias="StopLossRate", serialization_alias="StopLossRate")
    take_profit_rate: float | None = Field(None, alias="TakeProfitRate", serialization_alias="TakeProfitRate")
    is_tsl_enabled: bool | None = Field(None, alias="IsTslEnabled", serialization_alias="IsTslEnabled")
    is_no_stop_loss: bool | None = Field(None, alias="IsNoStopLoss", serialization_alias="IsNoStopLoss")
    is_no_take_profit: bool | None = Field(None, alias="IsNoTakeProfit", serialization_alias="IsNoTakeProfit")


class MarketOrderByUnitsRequest(BaseModel):
    instrument_id: int = Field(alias="InstrumentID", serialization_alias="InstrumentID")
    is_buy: bool = Field(alias="IsBuy", serialization_alias="IsBuy")
    leverage: int = Field(alias="Leverage", serialization_alias="Leverage")
    amount_in_units: float = Field(alias="AmountInUnits", serialization_alias="AmountInUnits")
    stop_loss_rate: float | None = Field(None, alias="StopLossRate", serialization_alias="StopLossRate")
    take_profit_rate: float | None = Field(None, alias="TakeProfitRate", serialization_alias="TakeProfitRate")
    is_tsl_enabled: bool | None = Field(None, alias="IsTslEnabled", serialization_alias="IsTslEnabled")
    is_no_stop_loss: bool | None = Field(None, alias="IsNoStopLoss", serialization_alias="IsNoStopLoss")
    is_no_take_profit: bool | None = Field(None, alias="IsNoTakeProfit", serialization_alias="IsNoTakeProfit")


class LimitOrderRequest(BaseModel):
    instrument_id: int = Field(alias="InstrumentID", serialization_alias="InstrumentID")
    is_buy: bool = Field(alias="IsBuy", serialization_alias="IsBuy")
    leverage: int = Field(alias="Leverage", serialization_alias="Leverage")
    amount: float | None = Field(None, alias="Amount", serialization_alias="Amount")
    amount_in_units: float | None = Field(None, alias="AmountInUnits", serialization_alias="AmountInUnits")
    rate: float = Field(alias="Rate", serialization_alias="Rate")
    stop_loss_rate: float = Field(alias="StopLossRate", serialization_alias="StopLossRate")
    take_profit_rate: float = Field(alias="TakeProfitRate", serialization_alias="TakeProfitRate")
    is_tsl_enabled: bool | None = Field(None, alias="IsTslEnabled", serialization_alias="IsTslEnabled")
    is_no_stop_loss: bool | None = Field(None, alias="IsNoStopLoss", serialization_alias="IsNoStopLoss")
    is_no_take_profit: bool | None = Field(None, alias="IsNoTakeProfit", serialization_alias="IsNoTakeProfit")


class ClosePositionRequest(BaseModel):
    instrument_id: int = Field(alias="InstrumentId", serialization_alias="InstrumentId")
    units_to_deduct: float | None = Field(None, alias="UnitsToDeduct", serialization_alias="UnitsToDeduct")



class OrderForOpen(BaseModel):
    instrument_id: int = Field(alias="instrumentID")
    amount: float
    is_buy: bool = Field(alias="isBuy")
    leverage: int
    stop_loss_rate: float = Field(0.0, alias="stopLossRate")
    take_profit_rate: float = Field(0.0, alias="takeProfitRate")
    is_tsl_enabled: bool = Field(False, alias="isTslEnabled")
    mirror_id: int = Field(0, alias="mirrorID")
    total_external_costs: float = Field(0.0, alias="totalExternalCosts")
    order_id: int = Field(alias="orderID")
    order_type: int = Field(alias="orderType")
    status_id: int = Field(alias="statusID")
    cid: int = Field(alias="CID")
    open_date_time: str = Field("", alias="openDateTime")
    last_update: str = Field("", alias="lastUpdate")


class OrderForOpenResponse(BaseModel):
    order_for_open: OrderForOpen = Field(alias="orderForOpen")
    token: str


class OrderForCloseResponse(BaseModel):
    token: str



class OrderPositionInfo(BaseModel):
    model_config = {"extra": "allow"}

    position_id: int = Field(alias="positionID")
    order_type: int = Field(alias="orderType")
    occurred: str
    rate: float
    units: float
    conversion_rate: float = Field(0.0, alias="conversionRate")
    amount: float
    is_open: bool = Field(alias="isOpen")


class OrderForOpenInfoResponse(BaseModel):
    model_config = {"extra": "allow"}

    token: str
    order_id: int = Field(alias="orderID")
    cid: int = Field(alias="CID")
    reference_id: str = Field("", alias="referenceID")
    status_id: int = Field(alias="statusID")
    order_type: int = Field(alias="orderType")
    open_action_type: int = Field(0, alias="openActionType")
    error_code: int | None = Field(None, alias="errorCode")
    error_message: str | None = Field(None, alias="errorMessage")
    instrument_id: int = Field(alias="instrumentID")
    amount: float
    units: float
    request_occurred: str = Field("", alias="requestOccurred")
    positions: list[OrderPositionInfo] = []



class Position(BaseModel):
    model_config = {"extra": "allow"}

    position_id: int = Field(alias="positionID")
    cid: int = Field(alias="CID")
    open_date_time: str = Field(alias="openDateTime")
    open_rate: float = Field(alias="openRate")
    instrument_id: int = Field(alias="instrumentID")
    is_buy: bool = Field(alias="isBuy")
    leverage: int
    take_profit_rate: float = Field(alias="takeProfitRate")
    stop_loss_rate: float = Field(alias="stopLossRate")
    mirror_id: int = Field(0, alias="mirrorID")
    parent_position_id: int = Field(0, alias="parentPositionID")
    amount: float
    order_id: int = Field(alias="orderID")
    order_type: int = Field(alias="orderType")
    units: float
    total_fees: float = Field(0.0, alias="totalFees")
    initial_amount_in_dollars: float = Field(0.0, alias="initialAmountInDollars")
    is_tsl_enabled: bool = Field(False, alias="isTslEnabled")
    stop_loss_version: int = Field(0, alias="stopLossVersion")
    is_settled: bool = Field(False, alias="isSettled")
    redeem_status_id: int = Field(0, alias="redeemStatusID")
    initial_units: float = Field(0.0, alias="initialUnits")
    is_partially_altered: bool = Field(False, alias="isPartiallyAltered")
    units_base_value_dollars: float = Field(0.0, alias="unitsBaseValueDollars")
    is_discounted: bool = Field(False, alias="isDiscounted")
    open_position_action_type: int = Field(0, alias="openPositionActionType")
    settlement_type_id: int = Field(0, alias="settlementTypeID")
    is_detached: bool = Field(False, alias="isDetached")
    open_conversion_rate: float = Field(0.0, alias="openConversionRate")
    pnl_version: int = Field(0, alias="pnlVersion")
    total_external_fees: float = Field(0.0, alias="totalExternalFees")
    total_external_taxes: float = Field(0.0, alias="totalExternalTaxes")
    is_no_take_profit: bool = Field(False, alias="isNoTakeProfit")
    is_no_stop_loss: bool = Field(False, alias="isNoStopLoss")
    lot_count: float = Field(0.0, alias="lotCount")



class PendingOrder(BaseModel):
    model_config = {"extra": "allow"}

    order_id: int = Field(alias="orderID")
    cid: int = Field(alias="CID")
    open_date_time: str = Field(alias="openDateTime")
    instrument_id: int = Field(alias="instrumentID")
    is_buy: bool = Field(alias="isBuy")
    take_profit_rate: float = Field(alias="takeProfitRate")
    stop_loss_rate: float = Field(alias="stopLossRate")
    rate: float
    amount: float
    leverage: int
    units: float
    is_tsl_enabled: bool = Field(False, alias="isTslEnabled")
    execution_type: int = Field(0, alias="executionType")



class Mirror(BaseModel):
    model_config = {"extra": "allow"}

    mirror_id: int = Field(alias="mirrorID")
    cid: int = Field(alias="CID")
    parent_cid: int = Field(alias="parentCID")
    stop_loss_percentage: float = Field(alias="stopLossPercentage")
    is_paused: bool = Field(alias="isPaused")
    copy_existing_positions: bool = Field(alias="copyExistingPositions")
    available_amount: float = Field(alias="availableAmount")
    stop_loss_amount: float = Field(alias="stopLossAmount")
    initial_investment: float = Field(alias="initialInvestment")
    deposit_summary: float = Field(alias="depositSummary")
    withdrawal_summary: float = Field(alias="withdrawalSummary")
    positions: list[Position] = []
    parent_username: str = Field("", alias="parentUsername")
    closed_positions_net_profit: float = Field(0.0, alias="closedPositionsNetProfit")
    started_copy_date: str = Field("", alias="startedCopyDate")
    pending_for_closure: bool = Field(False, alias="pendingForClosure")
    mirror_status_id: int = Field(0, alias="mirrorStatusID")
    orders_for_open: list[PendingOrder] = Field(default_factory=list, alias="ordersForOpen")
    orders_for_close: list[Any] = Field(default_factory=list, alias="ordersForClose")
    orders_for_close_multiple: list[Any] = Field(default_factory=list, alias="ordersForCloseMultiple")



class ClientPortfolio(BaseModel):
    positions: list[Position] = []
    credit: float = 0.0
    mirrors: list[Mirror] = []
    orders: list[PendingOrder] = []
    orders_for_open: list[PendingOrder] = Field(default_factory=list, alias="ordersForOpen")
    orders_for_close: list[Any] = Field(default_factory=list, alias="ordersForClose")
    orders_for_close_multiple: list[Any] = Field(default_factory=list, alias="ordersForCloseMultiple")
    bonus_credit: float = Field(0.0, alias="bonusCredit")


class PortfolioResponse(BaseModel):
    client_portfolio: ClientPortfolio = Field(alias="clientPortfolio")


class PnlResponse(BaseModel):
    client_portfolio: ClientPortfolio = Field(alias="clientPortfolio")



class TradeHistoryParams(BaseModel):
    min_date: str
    page: int | None = None
    page_size: int | None = None


class TradeHistoryEntry(BaseModel):
    net_profit: float = Field(alias="netProfit")
    close_rate: float = Field(alias="closeRate")
    close_timestamp: str = Field(alias="closeTimestamp")
    position_id: int = Field(alias="positionId")
    instrument_id: int = Field(alias="instrumentId")
    is_buy: bool = Field(alias="isBuy")
    leverage: int
    open_rate: float = Field(alias="openRate")
    open_timestamp: str = Field(alias="openTimestamp")
    stop_loss_rate: float = Field(alias="stopLossRate")
    take_profit_rate: float = Field(alias="takeProfitRate")
    trailing_stop_loss: bool = Field(alias="trailingStopLoss")
    order_id: int = Field(alias="orderId")
    social_trade_id: int = Field(0, alias="socialTradeId")
    parent_position_id: int = Field(0, alias="parentPositionId")
    investment: float
    initial_investment: float = Field(alias="initialInvestment")
    fees: float
    units: float

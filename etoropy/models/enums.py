from __future__ import annotations

from enum import IntEnum, StrEnum
from typing import Literal


class CandleInterval(StrEnum):
    ONE_MINUTE = "OneMinute"
    FIVE_MINUTES = "FiveMinutes"
    TEN_MINUTES = "TenMinutes"
    FIFTEEN_MINUTES = "FifteenMinutes"
    THIRTY_MINUTES = "ThirtyMinutes"
    ONE_HOUR = "OneHour"
    FOUR_HOURS = "FourHours"
    ONE_DAY = "OneDay"
    ONE_WEEK = "OneWeek"


class CandleDirection(StrEnum):
    ASC = "asc"
    DESC = "desc"


class OrderStatusId(IntEnum):
    PENDING = 1
    FILLING = 2
    EXECUTED = 3
    FAILED = 4
    CANCELLED = 5


class OrderType(IntEnum):
    MARKET = 1
    LIMIT = 2
    STOP = 3


class SettlementType(IntEnum):
    CFD = 0
    REAL_ASSET = 1
    SWAP = 2
    CRYPTO = 3
    FUTURE = 4


class MirrorStatus(IntEnum):
    ACTIVE = 0
    PAUSED = 1
    PENDING_CLOSURE = 2
    IN_ALIGNMENT = 3


TradingMode = Literal["demo", "real"]

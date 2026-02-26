from etoropy.models.enums import (
    CandleDirection,
    CandleInterval,
    MirrorStatus,
    OrderStatusId,
    OrderType,
    SettlementType,
)


def test_candle_interval_values() -> None:
    assert CandleInterval.ONE_MINUTE == "OneMinute"
    assert CandleInterval.FIVE_MINUTES == "FiveMinutes"
    assert CandleInterval.ONE_DAY == "OneDay"
    assert CandleInterval.ONE_WEEK == "OneWeek"


def test_candle_direction_values() -> None:
    assert CandleDirection.ASC == "asc"
    assert CandleDirection.DESC == "desc"


def test_order_status_id_values() -> None:
    assert OrderStatusId.PENDING == 1
    assert OrderStatusId.FILLING == 2
    assert OrderStatusId.EXECUTED == 3
    assert OrderStatusId.FAILED == 4
    assert OrderStatusId.CANCELLED == 5


def test_order_type_values() -> None:
    assert OrderType.MARKET == 1
    assert OrderType.LIMIT == 2
    assert OrderType.STOP == 3


def test_settlement_type_values() -> None:
    assert SettlementType.CFD == 0
    assert SettlementType.REAL_ASSET == 1
    assert SettlementType.CRYPTO == 3


def test_mirror_status_values() -> None:
    assert MirrorStatus.ACTIVE == 0
    assert MirrorStatus.PAUSED == 1

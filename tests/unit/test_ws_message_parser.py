from etoropy.models.websocket import WsEnvelope
from etoropy.ws.message_parser import parse_envelope, parse_messages


def test_parse_instrument_rate() -> None:
    envelope = WsEnvelope.model_validate(
        {
            "messages": [
                {
                    "topic": "instrument:1001",
                    "content": (
                        '{"Ask": 150.25, "Bid": 150.10, "LastExecution": 150.15,'
                        ' "Date": "2024-01-01", "PriceRateID": 123}'
                    ),
                    "id": "msg-1",
                    "type": "rate",
                }
            ]
        }
    )
    parsed = parse_messages(envelope)
    assert len(parsed) == 1
    assert parsed[0].type == "instrument:rate"
    assert parsed[0].data.instrument_id == 1001
    assert parsed[0].data.rate.ask == 150.25
    assert parsed[0].data.rate.bid == 150.10


def test_parse_private_event() -> None:
    envelope = WsEnvelope.model_validate(
        {
            "messages": [
                {
                    "topic": "private",
                    "content": (
                        '{"OrderID": 100, "OrderType": 1, "StatusID": 3,'
                        ' "InstrumentID": 1001, "CID": 200,'
                        ' "RequestedUnits": 1.0, "ExecutedUnits": 1.0,'
                        ' "NetProfit": 10.0, "CloseReason": "",'
                        ' "OpenDateTime": "2024-01-01",'
                        ' "RequestOccurred": "2024-01-01"}'
                    ),
                    "id": "msg-2",
                    "type": "event",
                }
            ]
        }
    )
    parsed = parse_messages(envelope)
    assert len(parsed) == 1
    assert parsed[0].type == "private:event"
    assert parsed[0].data.event.order_id == 100
    assert parsed[0].data.event.status_id == 3


def test_parse_unknown_topic() -> None:
    envelope = WsEnvelope.model_validate(
        {
            "messages": [
                {
                    "topic": "system:info",
                    "content": "{}",
                    "id": "msg-3",
                    "type": "info",
                }
            ]
        }
    )
    parsed = parse_messages(envelope)
    assert len(parsed) == 1
    assert parsed[0].type == "unknown"


def test_parse_instrument_heartbeat_skipped() -> None:
    """Messages with only Date+PriceRateID (no Ask/Bid) should be skipped."""
    envelope = WsEnvelope.model_validate(
        {
            "messages": [
                {
                    "topic": "instrument:100000",
                    "content": '{"Date": "2026-03-01T09:38:19Z", "PriceRateID": "133989539186"}',
                    "id": "msg-hb",
                    "type": "Trading.InstrumentRate",
                }
            ]
        }
    )
    parsed = parse_messages(envelope)
    assert len(parsed) == 0


def test_parse_envelope_from_string() -> None:
    raw = (
        '{"messages": [{"topic": "instrument:999",'
        ' "content": "{\\"Ask\\": 50.0, \\"Bid\\": 49.0}",'
        ' "id": "x", "type": "rate"}]}'
    )
    envelope = parse_envelope(raw)
    assert len(envelope.messages) == 1
    assert envelope.messages[0].topic == "instrument:999"

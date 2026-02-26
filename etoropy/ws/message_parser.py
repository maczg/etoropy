from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from ..models.websocket import WsEnvelope, WsInstrumentRate, WsPrivateEvent


@dataclass
class ParsedInstrumentRate:
    instrument_id: int
    rate: WsInstrumentRate


@dataclass
class ParsedPrivateEvent:
    event: WsPrivateEvent


@dataclass
class ParsedMessage:
    type: str  # "instrument:rate" | "private:event" | "unknown"
    data: ParsedInstrumentRate | ParsedPrivateEvent | Any = None


def parse_envelope(data: str) -> WsEnvelope:
    return WsEnvelope.model_validate(json.loads(data))


def parse_messages(envelope: WsEnvelope) -> list[ParsedMessage]:
    """Parse a WebSocket envelope into a list of typed messages.

    Recognises two topic patterns:

    - ``instrument:<id>`` -- parsed as ``instrument:rate`` with a
      ``ParsedInstrumentRate`` payload.
    - ``private`` -- parsed as ``private:event`` with a
      ``ParsedPrivateEvent`` payload (order status changes).

    Any other topic is returned as ``"unknown"``.
    """
    results: list[ParsedMessage] = []

    for msg in envelope.messages:
        if msg.topic.startswith("instrument:"):
            parts = msg.topic.split(":")
            instrument_id = int(parts[1])
            rate = WsInstrumentRate.model_validate(json.loads(msg.content))
            results.append(
                ParsedMessage(
                    type="instrument:rate",
                    data=ParsedInstrumentRate(instrument_id=instrument_id, rate=rate),
                )
            )
        elif msg.topic == "private":
            event = WsPrivateEvent.model_validate(json.loads(msg.content))
            results.append(
                ParsedMessage(
                    type="private:event",
                    data=ParsedPrivateEvent(event=event),
                )
            )
        else:
            results.append(ParsedMessage(type="unknown", data=msg))

    return results

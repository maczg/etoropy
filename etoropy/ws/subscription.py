from __future__ import annotations


class WsSubscriptionTracker:
    """Tracks active WebSocket topic subscriptions.

    Used internally by ``WsClient`` to re-subscribe to all topics
    after an automatic reconnection.
    """

    def __init__(self) -> None:
        self._subscriptions: set[str] = set()

    def add(self, topics: list[str]) -> None:
        self._subscriptions.update(topics)

    def remove(self, topics: list[str]) -> None:
        self._subscriptions.difference_update(topics)

    def get_all(self) -> list[str]:
        return list(self._subscriptions)

    def has(self, topic: str) -> bool:
        return topic in self._subscriptions

    def clear(self) -> None:
        self._subscriptions.clear()

    @property
    def size(self) -> int:
        return len(self._subscriptions)

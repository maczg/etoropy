from etoropy.ws.subscription import WsSubscriptionTracker


def test_add_and_get_all() -> None:
    tracker = WsSubscriptionTracker()
    tracker.add(["instrument:1001", "instrument:1002"])
    assert set(tracker.get_all()) == {"instrument:1001", "instrument:1002"}
    assert tracker.size == 2


def test_remove() -> None:
    tracker = WsSubscriptionTracker()
    tracker.add(["a", "b", "c"])
    tracker.remove(["b"])
    assert tracker.size == 2
    assert not tracker.has("b")
    assert tracker.has("a")


def test_clear() -> None:
    tracker = WsSubscriptionTracker()
    tracker.add(["a", "b"])
    tracker.clear()
    assert tracker.size == 0
    assert tracker.get_all() == []


def test_has() -> None:
    tracker = WsSubscriptionTracker()
    tracker.add(["topic1"])
    assert tracker.has("topic1")
    assert not tracker.has("topic2")


def test_duplicates() -> None:
    tracker = WsSubscriptionTracker()
    tracker.add(["a", "a", "b"])
    assert tracker.size == 2

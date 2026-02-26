import re

from etoropy._utils import generate_uuid


def test_generate_uuid_format() -> None:
    uid = generate_uuid()
    # UUID v4 format
    assert re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", uid)


def test_generate_uuid_unique() -> None:
    uids = {generate_uuid() for _ in range(100)}
    assert len(uids) == 100

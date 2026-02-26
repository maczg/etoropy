from __future__ import annotations

import uuid


def generate_uuid() -> str:
    return str(uuid.uuid4())

from __future__ import annotations

from typing import Any

from ..config.constants import API_PREFIX
from ._base import BaseRestClient


class PiDataClient(BaseRestClient):
    async def get_copiers_public_info(self) -> Any:
        """Get copier info for the authenticated user."""
        return await self._get(f"{API_PREFIX}/pi-data/copiers")

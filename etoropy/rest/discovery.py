from __future__ import annotations

from typing import Any, cast

from ..config.constants import API_PREFIX
from ._base import BaseRestClient


class DiscoveryClient(BaseRestClient):
    async def get_curated_lists(self) -> list[Any]:
        data = await self._get(f"{API_PREFIX}/curated-lists")
        if isinstance(data, dict) and "curatedLists" in data:
            return cast(list[Any], data["curatedLists"])
        if isinstance(data, dict) and "CuratedLists" in data:
            return cast(list[Any], data["CuratedLists"])
        if isinstance(data, list):
            return data
        return []

    async def get_market_recommendations(self) -> list[Any]:
        return cast(list[Any], await self._get(f"{API_PREFIX}/watchlists/recommendations"))

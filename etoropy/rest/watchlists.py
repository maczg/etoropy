from __future__ import annotations

from typing import Any

from ..config.constants import API_PREFIX
from ._base import BaseRestClient


class WatchlistsClient(BaseRestClient):
    async def get_user_watchlists(self) -> list[Any]:
        return await self._get(f"{API_PREFIX}/watchlists")

    async def get_watchlist(self, watchlist_id: int) -> Any:
        return await self._get(f"{API_PREFIX}/watchlists/{watchlist_id}")

    async def get_default_watchlist_items(self) -> list[Any]:
        return await self._get(f"{API_PREFIX}/watchlists/default/items")

    async def create_watchlist(self, name: str, items: list[int] | None = None) -> Any:
        body: dict[str, Any] = {"name": name}
        if items:
            body["items"] = items
        return await self._post(f"{API_PREFIX}/watchlists", body)

    async def create_default_watchlist(self, name: str, items: list[int] | None = None) -> Any:
        body: dict[str, Any] = {"name": name}
        if items:
            body["items"] = items
        return await self._post(f"{API_PREFIX}/watchlists/default", body)

    async def delete_watchlist(self, watchlist_id: int) -> None:
        await self._delete(f"{API_PREFIX}/watchlists/{watchlist_id}")

    async def rename_watchlist(self, watchlist_id: int, name: str) -> None:
        await self._put(f"{API_PREFIX}/watchlists/{watchlist_id}/name", {"name": name})

    async def set_default_watchlist(self, watchlist_id: int) -> None:
        await self._put(f"{API_PREFIX}/watchlists/{watchlist_id}/default")

    async def add_items(self, watchlist_id: int, instrument_ids: list[int]) -> None:
        await self._post(f"{API_PREFIX}/watchlists/{watchlist_id}/items", {"items": instrument_ids})

    async def remove_items(self, watchlist_id: int, instrument_ids: list[int]) -> None:
        await self._delete(f"{API_PREFIX}/watchlists/{watchlist_id}/items", {"items": instrument_ids})

    async def update_items(self, watchlist_id: int, instrument_ids: list[int]) -> None:
        await self._put(f"{API_PREFIX}/watchlists/{watchlist_id}/items", {"items": instrument_ids})

    async def change_rank(self, watchlist_id: int, rank: int) -> None:
        await self._put(f"{API_PREFIX}/watchlists/{watchlist_id}/rank", {"rank": rank})

    async def get_public_watchlists(self, user_id: int) -> list[Any]:
        return await self._get(f"{API_PREFIX}/watchlists/users/{user_id}/public")

    async def get_public_watchlist(self, watchlist_id: int) -> Any:
        return await self._get(f"{API_PREFIX}/watchlists/public/{watchlist_id}")

from __future__ import annotations

from typing import Any

from ..config.constants import API_PREFIX
from ._base import BaseRestClient


class FeedsClient(BaseRestClient):
    async def create_post(self, content: str, instrument_id: int | None = None) -> Any:
        body: dict[str, Any] = {"content": content}
        if instrument_id is not None:
            body["instrumentId"] = instrument_id
        return await self._post(f"{API_PREFIX}/feeds/posts", body)

    async def get_instrument_feed(
        self,
        instrument_id: int,
        *,
        take: int | None = None,
        offset: int | None = None,
    ) -> Any:
        query: dict[str, Any] = {}
        if take is not None:
            query["take"] = take
        if offset is not None:
            query["offset"] = offset
        return await self._get(f"{API_PREFIX}/feeds/instrument/{instrument_id}", query or None)

    async def get_user_feed(
        self,
        user_id: int,
        *,
        requester_user_id: int | str | None = None,
        take: int | None = None,
        offset: int | None = None,
    ) -> Any:
        query: dict[str, Any] = {}
        if requester_user_id is not None:
            query["requesterUserId"] = requester_user_id
        if take is not None:
            query["take"] = take
        if offset is not None:
            query["offset"] = offset
        return await self._get(f"{API_PREFIX}/feeds/user/{user_id}", query or None)

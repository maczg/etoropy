from __future__ import annotations

from typing import Any

from ..config.constants import API_PREFIX
from ..models.feeds import FeedResponse
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
        page: int | None = None,
        page_size: int | None = None,
    ) -> FeedResponse:
        query: dict[str, Any] = {}
        if page is not None:
            query["page"] = page
        if page_size is not None:
            query["pageSize"] = page_size
        data = await self._get(f"{API_PREFIX}/feeds/instruments/{instrument_id}", query or None)
        return FeedResponse.model_validate(data)

    async def get_user_feed(
        self,
        user_id: int,
        *,
        page: int | None = None,
        page_size: int | None = None,
    ) -> FeedResponse:
        query: dict[str, Any] = {}
        if page is not None:
            query["page"] = page
        if page_size is not None:
            query["pageSize"] = page_size
        data = await self._get(f"{API_PREFIX}/feeds/users/{user_id}", query or None)
        return FeedResponse.model_validate(data)

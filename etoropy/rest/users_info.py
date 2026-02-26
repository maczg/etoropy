from __future__ import annotations

from typing import Any

from ..config.constants import API_PREFIX
from ..models.feeds import UserPerformance, UserPortfolio, UserProfile
from ._base import BaseRestClient


class UsersInfoClient(BaseRestClient):
    async def search_users(
        self,
        *,
        search_text: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> Any:
        query: dict[str, Any] = {}
        if search_text is not None:
            query["searchText"] = search_text
        if page is not None:
            query["page"] = page
        if page_size is not None:
            query["pageSize"] = page_size
        return await self._get(f"{API_PREFIX}/users-info/search", query or None)

    async def get_user_profile(self, user_id: int) -> UserProfile:
        data = await self._get(f"{API_PREFIX}/users-info/{user_id}/profile")
        return UserProfile.model_validate(data)

    async def get_user_portfolio(self, user_id: int) -> UserPortfolio:
        data = await self._get(f"{API_PREFIX}/users-info/{user_id}/portfolio")
        return UserPortfolio.model_validate(data)

    async def get_user_trade_info(self, user_id: int) -> Any:
        return await self._get(f"{API_PREFIX}/users-info/{user_id}/trade-info")

    async def get_user_performance(self, user_id: int) -> UserPerformance:
        data = await self._get(f"{API_PREFIX}/users-info/{user_id}/performance")
        return UserPerformance.model_validate(data)

    async def get_user_performance_by_period(self, user_id: int, period: str) -> Any:
        return await self._get(f"{API_PREFIX}/users-info/{user_id}/performance/{period}")

from __future__ import annotations

from typing import Any

from ..config.constants import API_PREFIX
from ._base import BaseRestClient


class UsersInfoClient(BaseRestClient):
    async def search_users(
        self,
        *,
        search_text: str | None = None,
        period: str = "LastYear",
        page: int | None = None,
        page_size: int | None = None,
    ) -> Any:
        query: dict[str, Any] = {"period": period}
        if search_text is not None:
            query["searchText"] = search_text
        if page is not None:
            query["page"] = page
        if page_size is not None:
            query["pageSize"] = page_size
        return await self._get(f"{API_PREFIX}/user-info/people/search", query)

    async def get_user_profile(self, cid: int) -> Any:
        """Retrieve user profile by customer ID (cidList)."""
        data = await self._get(f"{API_PREFIX}/user-info/people", {"cidList": cid})
        if isinstance(data, dict) and "users" in data:
            users = data["users"]
            if users:
                return users[0]
        return data

    async def get_user_profile_by_username(self, username: str) -> Any:
        """Retrieve user profile by username."""
        data = await self._get(f"{API_PREFIX}/user-info/people", {"usernames": username})
        if isinstance(data, dict) and "users" in data:
            users = data["users"]
            if users:
                return users[0]
        return data

    async def get_user_portfolio(self, username: str) -> Any:
        """Retrieve a user's live public portfolio."""
        return await self._get(f"{API_PREFIX}/user-info/people/{username}/portfolio/live")

    async def get_user_trade_info(self, username: str) -> Any:
        return await self._get(f"{API_PREFIX}/user-info/people/{username}/trade-info")

    async def get_user_performance(self, username: str) -> Any:
        """Retrieve a user's monthly/yearly gain."""
        return await self._get(f"{API_PREFIX}/user-info/people/{username}/gain")

    async def get_user_performance_by_period(
        self,
        username: str,
        *,
        min_date: str,
        max_date: str,
        period_type: str = "Daily",
    ) -> Any:
        """Retrieve granular performance data (daily or period)."""
        return await self._get(
            f"{API_PREFIX}/user-info/people/{username}/daily-gain",
            {"minDate": min_date, "maxDate": max_date, "type": period_type},
        )

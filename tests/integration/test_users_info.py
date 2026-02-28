from __future__ import annotations

import pytest

from etoropy.rest.rest_client import RestClient

pytestmark = pytest.mark.integration


async def _find_user(rest_client: RestClient) -> dict:
    """Search for a user and return {cid, username} from the first result."""
    # Search without searchText (searchText causes 404 on this API)
    result = await rest_client.users_info.search_users(page_size=1)
    if not isinstance(result, dict):
        pytest.skip("Unexpected search response format")
    items = result.get("items", [])
    if not items:
        pytest.skip("No users found via search")
    item = items[0]
    # Get the username from the search result
    username = item.get("userName")
    if not username:
        pytest.skip("Could not extract userName from search results")
    # Get the CID via the profile endpoint
    profile = await rest_client.users_info.get_user_profile_by_username(username)
    if not isinstance(profile, dict):
        pytest.skip("Could not fetch user profile")
    cid = profile.get("realCID") or profile.get("gcid")
    if not cid:
        pytest.skip("Could not extract CID from profile")
    return {"cid": int(cid), "username": username}


class TestSearchUsers:
    async def test_returns_results(self, rest_client: RestClient) -> None:
        result = await rest_client.users_info.search_users(page_size=5)
        assert isinstance(result, dict)
        assert "items" in result
        assert len(result["items"]) > 0
        first = result["items"][0]
        assert "userName" in first


class TestGetUserProfile:
    async def test_returns_profile(self, rest_client: RestClient) -> None:
        # Use search to find a user, then fetch profile by CID
        search = await rest_client.users_info.search_users(page_size=1)
        username = search["items"][0]["userName"]
        profile = await rest_client.users_info.get_user_profile_by_username(username)
        assert isinstance(profile, dict)
        assert "gcid" in profile or "realCID" in profile
        assert profile.get("username") == username


class TestGetUserPortfolio:
    async def test_returns_portfolio(self, rest_client: RestClient) -> None:
        user = await _find_user(rest_client)
        result = await rest_client.users_info.get_user_portfolio(user["username"])
        assert isinstance(result, dict)


class TestGetUserPerformance:
    async def test_returns_performance(self, rest_client: RestClient) -> None:
        user = await _find_user(rest_client)
        result = await rest_client.users_info.get_user_performance(user["username"])
        assert isinstance(result, dict)
        assert "monthly" in result or "yearly" in result

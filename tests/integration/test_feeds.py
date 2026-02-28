from __future__ import annotations

import pytest

from etoropy.rest.rest_client import RestClient

from .conftest import AAPL_ID

pytestmark = pytest.mark.integration


class TestGetInstrumentFeed:
    async def test_returns_feed(self, rest_client: RestClient) -> None:
        result = await rest_client.feeds.get_instrument_feed(AAPL_ID, take=5)
        assert isinstance(result, (dict, list))

    async def test_instrument_feed_pagination(self, rest_client: RestClient) -> None:
        result = await rest_client.feeds.get_instrument_feed(AAPL_ID, take=2, offset=0)
        assert isinstance(result, (dict, list))


class TestGetUserFeed:
    async def test_returns_feed(self, rest_client: RestClient) -> None:
        # Search for a user, get their username, fetch profile for realCID
        search = await rest_client.users_info.search_users(page_size=1)
        username = search["items"][0]["userName"]
        profile = await rest_client.users_info.get_user_profile_by_username(username)
        real_cid = profile.get("realCID") or profile.get("gcid")
        result = await rest_client.feeds.get_user_feed(
            int(real_cid),
            requester_user_id=int(real_cid),
            take=5,
        )
        assert isinstance(result, dict)
        assert "discussions" in result

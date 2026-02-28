from __future__ import annotations

import pytest

from etoropy.rest.rest_client import RestClient

pytestmark = pytest.mark.integration


class TestGetUserWatchlists:
    async def test_returns_list(self, rest_client: RestClient) -> None:
        result = await rest_client.watchlists.get_user_watchlists()
        assert isinstance(result, list)


class TestGetDefaultWatchlistItems:
    async def test_returns_items(self, rest_client: RestClient) -> None:
        result = await rest_client.watchlists.get_default_watchlist_items()
        assert isinstance(result, list)

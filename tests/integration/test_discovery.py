from __future__ import annotations

import pytest

from etoropy.rest.rest_client import RestClient

pytestmark = pytest.mark.integration


class TestGetCuratedLists:
    async def test_returns_lists(self, rest_client: RestClient) -> None:
        result = await rest_client.discovery.get_curated_lists()
        assert isinstance(result, list)


class TestGetMarketRecommendations:
    async def test_returns_recommendations(self, rest_client: RestClient) -> None:
        try:
            result = await rest_client.discovery.get_market_recommendations()
        except Exception:
            pytest.skip("recommendations endpoint not available")
        assert isinstance(result, list)

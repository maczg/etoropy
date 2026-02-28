from __future__ import annotations

import pytest

from etoropy.errors.exceptions import EToroAuthError
from etoropy.rest.rest_client import RestClient

pytestmark = pytest.mark.integration


class TestGetCopiersPublicInfo:
    async def test_returns_copier_info(self, rest_client: RestClient) -> None:
        try:
            result = await rest_client.pi_data.get_copiers_public_info()
        except EToroAuthError:
            pytest.skip("pi-data/copiers requires Popular Investor permissions")
        assert isinstance(result, (dict, list))

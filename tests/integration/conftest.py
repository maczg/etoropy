from __future__ import annotations

import os

import pytest

from etoropy.config.settings import EToroConfig
from etoropy.http.client import HttpClient
from etoropy.rest.rest_client import RestClient
from etoropy.trading.client import EToroTrading

ETORO_API_KEY = os.environ.get("ETORO_API_KEY", "")
ETORO_USER_KEY = os.environ.get("ETORO_USER_KEY", "")

_credentials_set = bool(ETORO_API_KEY and ETORO_USER_KEY)

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not _credentials_set, reason="ETORO_API_KEY / ETORO_USER_KEY not set"),
]

# Well-known instrument IDs
AAPL_ID = 1001
TSLA_ID = 1111
MSFT_ID = 1004
BTC_ID = 100000


def _require_credentials() -> None:
    if not _credentials_set:
        pytest.skip("ETORO_API_KEY / ETORO_USER_KEY not set")


@pytest.fixture
def integration_config() -> EToroConfig:
    _require_credentials()
    return EToroConfig(
        api_key=ETORO_API_KEY,
        user_key=ETORO_USER_KEY,
        mode="demo",
        rate_limit=True,
        retry_attempts=3,
    )


@pytest.fixture
def http_client(integration_config: EToroConfig) -> HttpClient:
    return HttpClient(integration_config)


@pytest.fixture
def rest_client(integration_config: EToroConfig, http_client: HttpClient) -> RestClient:
    return RestClient(integration_config, http=http_client)


@pytest.fixture
def etoro(integration_config: EToroConfig) -> EToroTrading:
    client = EToroTrading(config=integration_config)
    client.resolver.load_bundled_csv()
    return client

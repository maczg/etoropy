from __future__ import annotations

from typing import Any

from ..config.settings import EToroConfig
from ..http.client import HttpClient
from .discovery import DiscoveryClient
from .feeds import FeedsClient
from .market_data import MarketDataClient
from .pi_data import PiDataClient
from .reactions import ReactionsClient
from .trading_execution import TradingExecutionClient
from .trading_info import TradingInfoClient
from .users_info import UsersInfoClient
from .watchlists import WatchlistsClient


class RestClient:
    """Facade that composes all eToro REST sub-clients.

    :ivar market_data: Instruments, rates, candles, exchanges (8 endpoints).
    :ivar execution: Open/close/cancel orders (7 endpoints, demo/real routing).
    :ivar info: Portfolio, PnL, order status, trade history (4 endpoints).
    :ivar watchlists: CRUD for watchlists (14 endpoints).
    :ivar feeds: Social feed posts per instrument/user (3 endpoints).
    :ivar reactions: Comment on posts (1 endpoint).
    :ivar discovery: Curated lists and recommendations (2 endpoints).
    :ivar pi_data: Copier public info (1 endpoint).
    :ivar users_info: User profiles, portfolios, performance (6 endpoints).
    """

    def __init__(self, config: EToroConfig, http: HttpClient | None = None) -> None:
        self._http = http or HttpClient(config)
        mode = config.mode

        self.market_data = MarketDataClient(self._http)
        self.execution = TradingExecutionClient(self._http, mode)
        self.info = TradingInfoClient(self._http, mode)
        self.feeds = FeedsClient(self._http)
        self.reactions = ReactionsClient(self._http)
        self.discovery = DiscoveryClient(self._http)
        self.pi_data = PiDataClient(self._http)
        self.watchlists = WatchlistsClient(self._http)
        self.users_info = UsersInfoClient(self._http)

    async def aclose(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> RestClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()

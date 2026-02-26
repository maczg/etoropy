"""etoropy - Python SDK for the eToro Public API."""

# High-level trading client
# Configuration
from .config.settings import EToroConfig

# Errors
from .errors.exceptions import (
    EToroApiError,
    EToroAuthError,
    EToroError,
    EToroRateLimitError,
    EToroValidationError,
    EToroWebSocketError,
)
from .http.client import HttpClient, RequestOptions
from .http.rate_limiter import RateLimiter, RateLimiterOptions

# Enums
from .models.enums import (
    CandleDirection,
    CandleInterval,
    MirrorStatus,
    OrderStatusId,
    OrderType,
    SettlementType,
)
from .rest.discovery import DiscoveryClient
from .rest.feeds import FeedsClient
from .rest.market_data import MarketDataClient
from .rest.pi_data import PiDataClient
from .rest.reactions import ReactionsClient

# Low-level clients
from .rest.rest_client import RestClient
from .rest.trading_execution import TradingExecutionClient
from .rest.trading_info import TradingInfoClient
from .rest.users_info import UsersInfoClient
from .rest.watchlists import WatchlistsClient
from .trading.client import EToroTrading, OrderOptions
from .trading.instrument_resolver import InstrumentInfo, InstrumentResolver

# WebSocket
from .ws.client import WsClient, WsClientOptions

__all__ = [
    # High-level
    "EToroTrading",
    "OrderOptions",
    "InstrumentInfo",
    "InstrumentResolver",
    # Low-level clients
    "RestClient",
    "HttpClient",
    "RequestOptions",
    "RateLimiter",
    "RateLimiterOptions",
    "MarketDataClient",
    "TradingExecutionClient",
    "TradingInfoClient",
    "FeedsClient",
    "ReactionsClient",
    "DiscoveryClient",
    "PiDataClient",
    "WatchlistsClient",
    "UsersInfoClient",
    # WebSocket
    "WsClient",
    "WsClientOptions",
    # Config
    "EToroConfig",
    # Enums
    "CandleDirection",
    "CandleInterval",
    "MirrorStatus",
    "OrderStatusId",
    "OrderType",
    "SettlementType",
    # Errors
    "EToroApiError",
    "EToroAuthError",
    "EToroError",
    "EToroRateLimitError",
    "EToroValidationError",
    "EToroWebSocketError",
]

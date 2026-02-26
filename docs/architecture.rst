Architecture
============

etoropy is organized in layers. The high-level
:class:`~etoropy.EToroTrading` client composes REST, WebSocket, and
instrument-resolution sub-systems and exposes a unified async API.

Layer diagram
-------------

.. code-block:: text

   +------------------------------------------------------+
   |  EToroTrading  (trading/client.py)                   |
   |  High-level: buy, sell, stream, wait_for_order       |
   +----+-----------------------------+-------------------+
        |                             |
   +----v-------------+   +-----------v-----------+
   |  RestClient      |   |  WsClient             |
   |  (9 sub-clients) |   |  auth, heartbeat,     |
   |                  |   |  reconnect, events    |
   +----+-------------+   +-----------+-----------+
        |                             |
   +----v-------------+   +-----------v-----------+
   |  HttpClient      |   |  websockets lib       |
   |  httpx + retry   |   |  (ping_interval for   |
   |  + rate limiter  |   |   heartbeat)          |
   +------------------+   +-----------------------+

Package layout
--------------

.. code-block:: text

   etoropy/
     __init__.py              # Public API exports
     _utils.py                # UUID generation
     config/
       settings.py            # EToroConfig (pydantic-settings)
       constants.py           # URLs, defaults, limits
     errors/
       exceptions.py          # 6-class error hierarchy
     models/
       enums.py               # CandleInterval, OrderStatusId, etc.
       common.py              # Pagination, TokenResponse
       market_data.py         # Instrument, Rate, Candle models
       trading.py             # Order, Position, Portfolio models
       feeds.py               # Social feed, user profile models
       websocket.py           # WsEnvelope, WsInstrumentRate, WsPrivateEvent
     http/
       client.py              # HttpClient (httpx wrapper with auth, retry, rate limiting)
       rate_limiter.py        # Token-bucket rate limiter
       retry.py               # Exponential backoff with jitter
     rest/
       _base.py               # BaseRestClient (GET/POST/PUT/DELETE helpers)
       rest_client.py         # RestClient facade (composes all sub-clients)
       market_data.py         # 8 endpoints
       trading_execution.py   # 7 endpoints (demo/real routing)
       trading_info.py        # 4 endpoints (demo/real routing)
       watchlists.py          # 14 endpoints
       feeds.py               # 3 endpoints
       reactions.py           # 1 endpoint
       discovery.py           # 2 endpoints
       pi_data.py             # 1 endpoint
       users_info.py          # 6 endpoints
     ws/
       client.py              # WsClient (auth, heartbeat, reconnect, events)
       message_parser.py      # Parse WS envelopes into typed events
       subscription.py        # Topic set tracking for reconnect re-subscribe
     trading/
       client.py              # EToroTrading (high-level entry point)
       instrument_resolver.py # Symbol <-> ID resolution (CSV + API)
     data/
       instruments.csv        # 5,200+ symbol mappings

REST sub-clients
----------------

The :class:`~etoropy.RestClient` facade composes nine specialized clients:

.. list-table::
   :header-rows: 1
   :widths: 30 10 60

   * - Client
     - Endpoints
     - Description
   * - :class:`~etoropy.MarketDataClient`
     - 8
     - Instruments, rates, candles, exchanges, industries
   * - :class:`~etoropy.TradingExecutionClient`
     - 7
     - Market/limit orders, close positions, cancel orders
   * - :class:`~etoropy.TradingInfoClient`
     - 4
     - Portfolio, P&L, order status, trade history
   * - :class:`~etoropy.WatchlistsClient`
     - 14
     - CRUD for user/public watchlists
   * - :class:`~etoropy.FeedsClient`
     - 3
     - Instrument/user feeds, post creation
   * - :class:`~etoropy.ReactionsClient`
     - 1
     - Comment creation
   * - :class:`~etoropy.DiscoveryClient`
     - 2
     - Curated lists, market recommendations
   * - :class:`~etoropy.UsersInfoClient`
     - 6
     - User profiles, portfolios, performance, search
   * - :class:`~etoropy.PiDataClient`
     - 1
     - Copier public info

WebSocket event system
----------------------

:class:`~etoropy.EToroTrading` exposes a Node.js-style event emitter:

.. list-table::
   :header-rows: 1
   :widths: 20 35 45

   * - Event
     - Callback signature
     - Description
   * - ``"price"``
     - ``(symbol, instrument_id, WsInstrumentRate)``
     - Live price tick
   * - ``"order:update"``
     - ``(WsPrivateEvent)``
     - Order status change
   * - ``"connected"``
     - ``()``
     - WebSocket connected and authenticated
   * - ``"disconnected"``
     - ``()``
     - Client disconnected
   * - ``"error"``
     - ``(Exception)``
     - Any error
   * - ``"ws:message"``
     - ``(WsEnvelope)``
     - Raw WebSocket envelope

Register handlers with :meth:`~etoropy.EToroTrading.on`,
:meth:`~etoropy.EToroTrading.off`, and
:meth:`~etoropy.EToroTrading.once`.

Instrument resolution
---------------------

The :class:`~etoropy.InstrumentResolver` translates human-readable symbols
(``"AAPL"``, ``"BTC"``) into eToro's integer instrument IDs through three
tiers:

1. **Bundled CSV** -- 5,200+ pre-mapped symbols loaded with
   ``load_bundled_csv()``. Instant, no network call.
2. **API exact match** -- queries ``/market-data/search`` by
   ``internalSymbolFull``.
3. **API text search** -- fallback free-text search on the same endpoint.

Results are cached in memory for the lifetime of the client.

Rate limiting & retry
---------------------

**Rate limiter**: Token-bucket algorithm (20 requests per 10-second window by
default). Automatically pauses outgoing requests when the bucket is full.
Honors ``Retry-After`` headers from 429 responses.

**Retry**: Exponential backoff with jitter (+-25%). Retries on:

- HTTP 429 (rate limit)
- HTTP 5xx (server error)
- Connection errors and read timeouts

Default: 3 attempts, 1-second base delay, 2x backoff multiplier.

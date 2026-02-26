Changelog
=========

v0.1.0 (2025)
--------------

Initial release.

- 42+ REST endpoints across 9 sub-clients (market data, trading execution,
  trading info, watchlists, feeds, reactions, discovery, user info, PI data)
- Real-time WebSocket streaming with auto-reconnect and heartbeat
- :class:`~etoropy.EToroTrading` high-level client with event emitter
- :class:`~etoropy.InstrumentResolver` with bundled 5,200+ symbol CSV
- Token-bucket rate limiter and exponential-backoff retry
- Full type hints (mypy strict) and Pydantic v2 models
- Demo and real trading mode support

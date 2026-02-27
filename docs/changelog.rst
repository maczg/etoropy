Changelog
=========

v0.1.4 (2026-02-27)
--------------------

- Fix ``ValidationError`` on candle volume: allow ``None`` from API responses
  where volume data is unavailable

v0.1.3 (2026-02-27)
--------------------

- Make rate limiter configurable via ``EToroConfig`` fields and environment
  variables (``ETORO_RATE_LIMIT``, ``ETORO_RATE_LIMIT_MAX_REQUESTS``,
  ``ETORO_RATE_LIMIT_WINDOW``)
- Allow disabling rate limiting entirely by setting ``rate_limit=False``
- ``HttpClient`` now builds ``RateLimiterOptions`` from config when no explicit
  ``rate_limiter`` argument is provided

v0.1.2 (2026-02-26)
--------------------

- Fix WebSocket auth deadlock: start receive loop before ``_authenticate()``
- Fix binary frame handling: skip bytes messages, pass text directly without
  ``str()`` wrapping
- Add 15 unit tests for ``WsClient`` (event emitter, auth flow, binary frames,
  disconnect, error paths)
- Migrate ``.claude/commands/`` templates from npm/Node.js to Python tooling

v0.1.1 (2026-02-26)
--------------------

- Add Sphinx documentation site with Furo theme and autodoc API reference
- Add quickstart, architecture, and examples guides
- Add GitHub Actions workflow for automatic docs deploy to GitHub Pages

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

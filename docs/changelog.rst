Changelog
=========

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

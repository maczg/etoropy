# etoropy

Python SDK for the [eToro Public API](https://www.etoro.com/). Async-first, fully typed, built for algo trading.

> [!WARNING]  
> **Alpha software** ⚠️ This package is under active development and its API may
> change without notice. Use at your own risk. The authors accept no
> responsibility for any financial losses incurred through the use of this
> software. Always test thoroughly in demo mode before trading with real funds.

Covers **42+ REST endpoints**, **real-time WebSocket streaming**, instrument resolution from a bundled 5,200+ symbol CSV,
token-bucket rate limiting, and exponential-backoff retry, all behind a single `EToroTrading` entry point.

## Requirements

- Python 3.11+
- An eToro Public API key pair (`api_key` + `user_key`)

## Installation

```bash
pip install etoropy
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add etoropy
```

## Configuration

The SDK reads configuration from environment variables (prefix `ETORO_`) or accepts them directly in code.

### Environment variables

Create a `.env` file (see `.env.example`):

```env
ETORO_API_KEY=your-api-key
ETORO_USER_KEY=your-user-key
ETORO_MODE=demo          # "demo" or "real"
ETORO_BASE_URL=https://public-api.etoro.com
ETORO_WS_URL=wss://ws.etoro.com/ws
```

### In code

```python
from etoropy import EToroConfig, EToroTrading

config = EToroConfig(
    api_key="your-api-key",
    user_key="your-user-key",
    mode="demo",           # default
    timeout=30.0,          # HTTP timeout in seconds
    retry_attempts=3,      # retries on 5xx / rate-limit / connection errors
    retry_delay=1.0,       # base delay between retries (exponential backoff)
)
etoro = EToroTrading(config=config)
```

`EToroConfig` is a [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) `BaseSettings` subclass, so any field can be set via its `ETORO_`-prefixed env var.

## Quick start

```python
import asyncio
from etoropy import EToroTrading, OrderOptions

async def main():
    async with EToroTrading() as etoro:
        # Load the bundled CSV for instant symbol -> instrument ID resolution
        etoro.resolver.load_bundled_csv()

        # Fetch live rates
        rates = await etoro.get_rates(["AAPL", "TSLA", "BTC"])
        for r in rates:
            symbol = etoro.resolver.get_symbol(r.instrument_id) or str(r.instrument_id)
            print(f"{symbol}: bid={r.bid}, ask={r.ask}")

        # Place a buy order (demo mode)
        result = await etoro.buy_by_amount(
            "AAPL",
            amount=100.0,
            options=OrderOptions(leverage=1, stop_loss=100.0, take_profit=200.0),
        )
        print(f"Order ID: {result.order_for_open.order_id}")

asyncio.run(main())
```

## Trading

All trading methods accept a symbol string (`"AAPL"`) or an integer instrument ID. The SDK resolves symbols automatically.

### Market orders

```python
# Buy / Sell by dollar amount
await etoro.buy_by_amount("AAPL", amount=500.0, options=OrderOptions(leverage=2))
await etoro.sell_by_amount("TSLA", amount=200.0)

# Buy / Sell by units
await etoro.buy_by_units("BTC", units=0.01)
await etoro.sell_by_units("ETH", units=1.5)
```

### Limit orders

```python
from etoropy import OrderOptions

token = await etoro.place_limit_order(
    "AAPL",
    is_buy=True,
    trigger_rate=140.0,
    amount=500.0,
    options=OrderOptions(leverage=1, stop_loss=130.0, take_profit=160.0),
)
```

### Close positions

```python
# Close a single position (optionally partial close with units_to_deduct)
await etoro.close_position(position_id=123456)
await etoro.close_position(position_id=123456, units_to_deduct=0.5)

# Close everything
await etoro.close_all_positions()
```

### Cancel orders

```python
await etoro.cancel_order(order_id)
await etoro.cancel_limit_order(order_id)
await etoro.cancel_all_orders()
await etoro.cancel_all_limit_orders()
```

### Wait for order execution

`wait_for_order` combines a WebSocket listener with a REST polling fallback. It returns the execution event or raises on failure/timeout.

```python
result = await etoro.buy_by_amount("AAPL", 100.0)
order_id = result.order_for_open.order_id

# Blocks until the order executes, fails, or times out
event = await etoro.wait_for_order(order_id, timeout_s=15.0)
print(f"Executed! Position ID: {event.position_id}")
```

Internally, the method subscribes to private WebSocket events and, after a 3-second grace period, starts polling the REST order status endpoint as a fallback.

## Portfolio & Market Data

### Portfolio

```python
portfolio = await etoro.get_portfolio()
positions = await etoro.get_positions()
pending = await etoro.get_pending_orders()
pnl = await etoro.get_pnl()
history = await etoro.get_trade_history(min_date="2025-01-01", page=1, page_size=50)
```

### Market data

```python
from etoropy import CandleInterval, CandleDirection

# Live rates (fan-out: one request per instrument -- the API rejects comma-separated IDs)
rates = await etoro.get_rates(["AAPL", "TSLA", "BTC"])

# Historical candles
candles = await etoro.get_candles(
    "AAPL",
    interval=CandleInterval.ONE_DAY,
    count=30,
    direction=CandleDirection.DESC,
)
```

## WebSocket Streaming

The SDK uses `websockets` for real-time price updates and private account events.

### Stream prices

```python
from etoropy.models.websocket import WsInstrumentRate

def on_price(symbol: str, instrument_id: int, rate: WsInstrumentRate):
    print(f"{symbol}: bid={rate.bid}, ask={rate.ask}")

etoro.on("price", on_price)
await etoro.connect()
await etoro.stream_prices(["AAPL", "TSLA", "BTC"])
```

### Private events (order updates)

```python
from etoropy.models.websocket import WsPrivateEvent

def on_order(event: WsPrivateEvent):
    print(f"Order {event.order_id}: status={event.status_id}")

etoro.on("order:update", on_order)
etoro.subscribe_to_private_events()
```

### Events reference

| Event | Callback signature | Description |
|---|---|---|
| `"price"` | `(symbol: str, instrument_id: int, rate: WsInstrumentRate)` | Live price tick |
| `"order:update"` | `(event: WsPrivateEvent)` | Order status change |
| `"connected"` | `()` | WebSocket connected and authenticated |
| `"disconnected"` | `()` | Client disconnected |
| `"error"` | `(error: Exception)` | Any error |
| `"ws:message"` | `(envelope: WsEnvelope)` | Raw WebSocket envelope |

### Event methods

```python
etoro.on("price", handler)       # register
etoro.off("price", handler)      # unregister
etoro.once("price", handler)     # fire once then auto-unregister
etoro.remove_all_listeners()     # clear all
```

## Instrument Resolution

The `InstrumentResolver` translates human-readable symbols (`"AAPL"`, `"BTC"`) into eToro's integer instrument IDs. It resolves through three tiers:

1. **Bundled CSV** -- 5,200+ pre-mapped symbols loaded with `load_bundled_csv()`. Instant, no network call.
2. **API exact match** -- queries `/market-data/search` by `internalSymbolFull`.
3. **API text search** -- fallback free-text search on the same endpoint.

Results are cached in memory for the lifetime of the client.

```python
# Load the CSV (recommended at startup)
etoro.resolver.load_bundled_csv()

# Resolve a symbol
instrument_id = await etoro.resolve_instrument("AAPL")

# Get display metadata
info = await etoro.get_instrument_info("AAPL")
print(info.display_name)  # "Apple Inc"
print(info.symbol_full)   # "AAPL"
print(info.exchange_id)   # 1 (NASDAQ)

# Batch metadata
infos = await etoro.get_instrument_info_batch(["AAPL", "TSLA", "GOOG"])

# Preload symbols for fast lookup later
await etoro.preload_instruments(["AAPL", "TSLA", "BTC", "ETH"])
```

## Low-Level REST Clients

For finer control, access the individual REST clients through `etoro.rest`:

```python
# Direct access to the RestClient facade
rest = etoro.rest

# Market data (8 endpoints)
await rest.market_data.search_instruments(fields="instrumentId", search_text="Apple")
await rest.market_data.get_instruments(instrument_ids=[1001])
await rest.market_data.get_rates([1001, 1002])
await rest.market_data.get_candles(1001, "desc", "OneDay", 30)
await rest.market_data.get_instrument_types()
await rest.market_data.get_closing_prices()
await rest.market_data.get_stocks_industries()
await rest.market_data.get_exchanges()

# Trading execution (7 endpoints, auto-routes demo/real)
await rest.execution.open_market_order_by_amount(params)
await rest.execution.open_market_order_by_units(params)
await rest.execution.open_limit_order(params)
await rest.execution.close_position(position_id, params)
await rest.execution.cancel_market_open_order(order_id)
await rest.execution.cancel_limit_order(order_id)
await rest.execution.cancel_close_order(order_id)

# Trading info (4 endpoints)
await rest.info.get_portfolio()
await rest.info.get_pnl()
await rest.info.get_order(order_id)
await rest.info.get_trade_history("2025-01-01")

# Watchlists (14 endpoints)
await rest.watchlists.get_user_watchlists()
await rest.watchlists.create_watchlist("My List", items=[1001, 1002])
await rest.watchlists.add_items(watchlist_id, [1003])
# ... rename, delete, reorder, get public watchlists, etc.

# Social feeds (3 endpoints)
await rest.feeds.get_instrument_feed(instrument_id=1001)
await rest.feeds.get_user_feed(user_id=12345)
await rest.feeds.create_post("Hello eToro!")

# Reactions (1 endpoint)
await rest.reactions.create_comment(post_id="abc", content="Nice trade!")

# Discovery (2 endpoints)
await rest.discovery.get_curated_lists()
await rest.discovery.get_market_recommendations()

# User info (6 endpoints)
await rest.users_info.get_user_profile(user_id)
await rest.users_info.get_user_portfolio(user_id)
await rest.users_info.get_user_performance(user_id)
await rest.users_info.search_users(search_text="warren")
# ...

# PI data (1 endpoint)
await rest.pi_data.get_copiers_public_info(user_id)
```

## Error Handling

All SDK errors inherit from `EToroError`:

```
EToroError
  +-- EToroApiError           # HTTP 4xx/5xx (has .status_code, .response_body, .request_id)
  |     +-- EToroRateLimitError   # HTTP 429 (has .retry_after_s)
  +-- EToroAuthError          # HTTP 401/403 or WS auth failure
  +-- EToroValidationError    # Invalid input (has .field)
  +-- EToroWebSocketError     # WS connection/protocol errors
```

```python
from etoropy import EToroApiError, EToroRateLimitError, EToroAuthError

try:
    await etoro.buy_by_amount("AAPL", 100.0)
except EToroRateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after_s}s")
except EToroAuthError:
    print("Check your API key / user key")
except EToroApiError as e:
    print(f"API error {e.status_code}: {e.response_body}")
```

## Rate Limiting & Retry

**Rate limiter**: Token-bucket algorithm (20 requests per 10-second window by default). Automatically pauses outgoing requests when the bucket is full. Honors `Retry-After` headers from 429 responses.

**Retry**: Exponential backoff with jitter (+-25%). Retries on:
- HTTP 429 (rate limit)
- HTTP 5xx (server error)
- Connection errors and read timeouts

Default: 3 attempts, 1-second base delay, 2x backoff multiplier.

## Architecture

```
etoropy/
  __init__.py              # Public API (33 exports)
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
```

### Layer diagram

```
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
```

## Logging

The SDK logs to the `"etoropy"` logger. Configure it with standard `logging`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("etoropy").setLevel(logging.INFO)
```

## Development

```bash
# Clone and install
git clone <repo-url> && cd etoropy
uv sync

# Run tests
uv run pytest

# Lint
uv run ruff check etoropy/

# Type check
uv run mypy etoropy/
```

## Disclaimer

This software is provided "as is", without warranty of any kind. Trading
financial instruments carries risk. You are solely responsible for any
trades executed through this SDK. The authors and contributors shall not be
held liable for any losses, damages, or other liabilities arising from its
use. Always validate behavior in **demo mode** before connecting to a real
account.

## Credits

This project is a Python port of [etoro-sdk](https://github.com/shayhe-tr/etoro-sdk) by [@shayhe-tr](https://github.com/shayhe-tr), originally written in TypeScript. Full credit for the API design, endpoint mapping, and instrument CSV goes to the original author.

## License

MIT
Quickstart
==========

Requirements
------------

- Python 3.11+
- An eToro Public API key pair (``api_key`` + ``user_key``)

Installation
------------

.. code-block:: bash

   pip install etoropy

Or with `uv <https://docs.astral.sh/uv/>`_:

.. code-block:: bash

   uv add etoropy

Configuration
-------------

The SDK reads configuration from environment variables (prefix ``ETORO_``)
or accepts them directly in code.

**Environment variables**

Create a ``.env`` file:

.. code-block:: bash

   ETORO_API_KEY=your-api-key
   ETORO_USER_KEY=your-user-key
   ETORO_MODE=demo          # "demo" or "real"
   ETORO_BASE_URL=https://public-api.etoro.com
   ETORO_WS_URL=wss://ws.etoro.com/ws

**In code**

.. code-block:: python

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

:class:`~etoropy.EToroConfig` is a
`pydantic-settings <https://docs.pydantic.dev/latest/concepts/pydantic_settings/>`_
``BaseSettings`` subclass, so any field can be set via its ``ETORO_``-prefixed
environment variable.

First API call
--------------

.. code-block:: python

   import asyncio
   from etoropy import EToroTrading, OrderOptions

   async def main():
       async with EToroTrading() as etoro:
           # Load bundled instrument mappings for fast symbol resolution
           etoro.resolver.load_bundled_csv()

           # Fetch live rates
           rates = await etoro.get_rates(["AAPL", "TSLA", "BTC"])
           for r in rates:
               symbol = etoro.resolver.get_symbol(r.instrument_id) or str(r.instrument_id)
               print(f"{symbol}: bid={r.bid}, ask={r.ask}")

           # Place a market buy order (demo mode)
           result = await etoro.buy_by_amount(
               "AAPL",
               amount=100.0,
               options=OrderOptions(leverage=1, stop_loss=100.0, take_profit=200.0),
           )
           print(f"Order ID: {result.order_for_open.order_id}")

   asyncio.run(main())

Trading basics
--------------

All trading methods accept a symbol string (``"AAPL"``) or an integer
instrument ID. The SDK resolves symbols automatically.

**Market orders**

.. code-block:: python

   # Buy / Sell by dollar amount
   await etoro.buy_by_amount("AAPL", amount=500.0, options=OrderOptions(leverage=2))
   await etoro.sell_by_amount("TSLA", amount=200.0)

   # Buy / Sell by units
   await etoro.buy_by_units("BTC", units=0.01)
   await etoro.sell_by_units("ETH", units=1.5)

**Limit orders**

.. code-block:: python

   from etoropy import OrderOptions

   token = await etoro.place_limit_order(
       "AAPL",
       is_buy=True,
       trigger_rate=140.0,
       amount=500.0,
       options=OrderOptions(leverage=1, stop_loss=130.0, take_profit=160.0),
   )

**Close positions**

.. code-block:: python

   await etoro.close_position(position_id=123456)
   await etoro.close_position(position_id=123456, units_to_deduct=0.5)  # partial
   await etoro.close_all_positions()

**Cancel orders**

.. code-block:: python

   await etoro.cancel_order(order_id)
   await etoro.cancel_limit_order(order_id)
   await etoro.cancel_all_orders()
   await etoro.cancel_all_limit_orders()

Error handling
--------------

All SDK errors inherit from :class:`~etoropy.EToroError`:

.. code-block:: python

   from etoropy import EToroApiError, EToroRateLimitError, EToroAuthError

   try:
       await etoro.buy_by_amount("AAPL", 100.0)
   except EToroRateLimitError as e:
       print(f"Rate limited. Retry after {e.retry_after_s}s")
   except EToroAuthError:
       print("Check your API key / user key")
   except EToroApiError as e:
       print(f"API error {e.status_code}: {e.response_body}")

Logging
-------

The SDK logs to the ``"etoropy"`` logger. Configure it with standard
:mod:`logging`:

.. code-block:: python

   import logging
   logging.basicConfig(level=logging.DEBUG)
   logging.getLogger("etoropy").setLevel(logging.INFO)

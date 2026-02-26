Examples
========

The examples below are taken from the ``examples/`` directory in the
repository. Each is a standalone script that you can run with:

.. code-block:: bash

   uv run python examples/<script>.py

Make sure you have ``ETORO_API_KEY`` and ``ETORO_USER_KEY`` set in your
environment (or in a ``.env`` file).

Basic usage
-----------

Fetch live rates and place a market order.

.. literalinclude:: ../examples/basic_usage.py
   :language: python
   :caption: examples/basic_usage.py

Stream prices
-------------

Subscribe to real-time WebSocket price updates.

.. literalinclude:: ../examples/stream_prices.py
   :language: python
   :caption: examples/stream_prices.py

Algo bot skeleton
-----------------

A minimal framework for building an event-driven trading bot.

.. literalinclude:: ../examples/algo_bot_skeleton.py
   :language: python
   :caption: examples/algo_bot_skeleton.py

Portfolio & market data
-----------------------

.. code-block:: python

   import asyncio
   from etoropy import EToroTrading, CandleInterval, CandleDirection

   async def main():
       async with EToroTrading() as etoro:
           etoro.resolver.load_bundled_csv()

           # Portfolio
           portfolio = await etoro.get_portfolio()
           positions = await etoro.get_positions()
           pending = await etoro.get_pending_orders()
           pnl = await etoro.get_pnl()
           history = await etoro.get_trade_history(
               min_date="2025-01-01", page=1, page_size=50,
           )

           # Historical candles
           candles = await etoro.get_candles(
               "AAPL",
               interval=CandleInterval.ONE_DAY,
               count=30,
               direction=CandleDirection.DESC,
           )

   asyncio.run(main())

Wait for order execution
------------------------

The :meth:`~etoropy.EToroTrading.wait_for_order` method combines a WebSocket
listener with a REST polling fallback:

.. code-block:: python

   import asyncio
   from etoropy import EToroTrading

   async def main():
       async with EToroTrading() as etoro:
           etoro.resolver.load_bundled_csv()
           await etoro.connect()

           result = await etoro.buy_by_amount("AAPL", 100.0)
           order_id = result.order_for_open.order_id

           # Blocks until the order executes, fails, or times out
           event = await etoro.wait_for_order(order_id, timeout_s=15.0)
           print(f"Executed! Position ID: {event.position_id}")

   asyncio.run(main())

Low-level REST clients
----------------------

For finer control, access the individual REST sub-clients through
``etoro.rest``:

.. code-block:: python

   import asyncio
   from etoropy import EToroTrading

   async def main():
       async with EToroTrading() as etoro:
           rest = etoro.rest

           # Market data
           result = await rest.market_data.search_instruments(
               fields="instrumentId", search_text="Apple",
           )

           # Watchlists
           watchlists = await rest.watchlists.get_user_watchlists()

           # Social feeds
           feed = await rest.feeds.get_instrument_feed(instrument_id=1001)

           # User info
           profile = await rest.users_info.get_user_profile(user_id=12345)

   asyncio.run(main())

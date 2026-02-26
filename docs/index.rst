etoropy
=======

Python SDK for the `eToro Public API <https://www.etoro.com/>`_.
Async-first, fully typed, built for algo trading.

.. warning::

   **Alpha software** -- This package is under active development and its API
   may change without notice. Use at your own risk. The authors accept no
   responsibility for any financial losses incurred through the use of this
   software. Always test thoroughly in demo mode before trading with real funds.

Covers **42+ REST endpoints**, **real-time WebSocket streaming**, instrument
resolution from a bundled 5,200+ symbol CSV, token-bucket rate limiting, and
exponential-backoff retry -- all behind a single :class:`~etoropy.EToroTrading`
entry point.

.. code-block:: python

   import asyncio
   from etoropy import EToroTrading

   async def main():
       async with EToroTrading() as etoro:
           etoro.resolver.load_bundled_csv()
           rates = await etoro.get_rates(["AAPL", "TSLA", "BTC"])
           for r in rates:
               symbol = etoro.resolver.get_symbol(r.instrument_id) or str(r.instrument_id)
               print(f"{symbol}: bid={r.bid}, ask={r.ask}")

   asyncio.run(main())

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   quickstart
   architecture
   examples
   changelog

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/index

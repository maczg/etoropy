"""Basic usage of the etoropy SDK."""

import asyncio

from etoropy import EToroTrading, OrderOptions


async def main() -> None:
    # Config is loaded from environment variables (ETORO_API_KEY, ETORO_USER_KEY, etc.)
    # Or pass them directly:
    async with EToroTrading() as etoro:
        # Load bundled instrument mappings for fast symbol resolution
        etoro.resolver.load_bundled_csv()

        # Get live rates for some instruments
        rates = await etoro.get_rates(["AAPL", "TSLA", "BTC"])
        for rate in rates:
            symbol = etoro.resolver.get_symbol(rate.instrument_id) or str(rate.instrument_id)
            print(f"{symbol}: bid={rate.bid}, ask={rate.ask}")

        # Get portfolio
        portfolio = await etoro.get_portfolio()
        print(f"Positions: {len(portfolio.client_portfolio.positions)}")
        print(f"Credit: {portfolio.client_portfolio.credit}")

        # Place a market order (demo mode)
        result = await etoro.buy_by_amount(
            "AAPL",
            amount=100.0,
            options=OrderOptions(leverage=1, stop_loss=100.0, take_profit=200.0),
        )
        print(f"Order placed: {result.order_for_open.order_id}")


if __name__ == "__main__":
    asyncio.run(main())

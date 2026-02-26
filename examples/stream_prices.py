"""Stream live prices via WebSocket."""

import asyncio

from etoropy import EToroTrading
from etoropy.models.websocket import WsInstrumentRate


async def main() -> None:
    async with EToroTrading() as etoro:
        etoro.resolver.load_bundled_csv()

        # Listen for price updates
        def on_price(symbol: str, instrument_id: int, rate: WsInstrumentRate) -> None:
            print(f"{symbol} ({instrument_id}): bid={rate.bid}, ask={rate.ask}")

        etoro.on("price", on_price)

        # Connect WebSocket
        await etoro.connect()

        # Start streaming prices
        await etoro.stream_prices(["AAPL", "TSLA", "BTC"])

        # Stream for 60 seconds
        await asyncio.sleep(60)

        # Stop streaming
        await etoro.stop_streaming_prices(["AAPL", "TSLA", "BTC"])


if __name__ == "__main__":
    asyncio.run(main())

"""Skeleton for an algorithmic trading bot using etoropy."""

import asyncio
import logging

from etoropy import EToroTrading, OrderOptions
from etoropy.models.websocket import WsInstrumentRate, WsPrivateEvent

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("algo-bot")


class SimpleBot:
    def __init__(self) -> None:
        self.etoro = EToroTrading()
        self.etoro.resolver.load_bundled_csv()
        self._running = False

    async def start(self) -> None:
        logger.info("Starting bot...")
        self._running = True

        # Register event handlers
        self.etoro.on("price", self.on_price)
        self.etoro.on("order:update", self.on_order_update)
        self.etoro.on("error", self.on_error)

        # Connect
        await self.etoro.connect()

        # Subscribe to private events (order updates)
        self.etoro.subscribe_to_private_events()

        # Stream prices for instruments of interest
        await self.etoro.stream_prices(["AAPL", "BTC"])

        logger.info("Bot running. Press Ctrl+C to stop.")

        # Keep running
        try:
            while self._running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        finally:
            await self.stop()

    async def stop(self) -> None:
        self._running = False
        logger.info("Stopping bot...")
        await self.etoro.disconnect()
        logger.info("Bot stopped.")

    def on_price(self, symbol: str, instrument_id: int, rate: WsInstrumentRate) -> None:
        mid_price = (rate.bid + rate.ask) / 2
        logger.info("Price update: %s = %.4f (bid=%.4f, ask=%.4f)", symbol, mid_price, rate.bid, rate.ask)

        # --- YOUR STRATEGY LOGIC HERE ---
        # Example: simple threshold trigger
        # if symbol == "AAPL" and mid_price < 150.0:
        #     asyncio.create_task(self.place_buy("AAPL", 100.0))

    def on_order_update(self, event: WsPrivateEvent) -> None:
        logger.info(
            "Order update: OrderID=%d, Status=%d, InstrumentID=%d",
            event.order_id,
            event.status_id,
            event.instrument_id,
        )

    def on_error(self, error: Exception) -> None:
        logger.error("Error: %s", error)

    async def place_buy(self, symbol: str, amount: float) -> None:
        try:
            result = await self.etoro.buy_by_amount(symbol, amount, OrderOptions(leverage=1))
            order_id = result.order_for_open.order_id
            logger.info("Buy order placed: %d", order_id)

            # Wait for execution
            event = await self.etoro.wait_for_order(order_id, timeout_s=10.0)
            logger.info("Order executed: position_id=%s", event.position_id)
        except Exception as e:
            logger.error("Failed to place buy order: %s", e)


async def main() -> None:
    bot = SimpleBot()
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())

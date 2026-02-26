import pytest

from etoropy.trading.instrument_resolver import InstrumentResolver


def test_load_bundled_csv() -> None:
    """Test that the bundled CSV loads and contains reasonable data."""
    from unittest.mock import AsyncMock

    mock_market_data = AsyncMock()
    resolver = InstrumentResolver(mock_market_data)
    loaded = resolver.load_bundled_csv()
    assert loaded > 5000  # CSV has 5200+ entries


def test_register_and_lookup() -> None:
    from unittest.mock import AsyncMock

    mock_market_data = AsyncMock()
    resolver = InstrumentResolver(mock_market_data)
    resolver.register("AAPL", 1001)
    assert resolver.get_cached_id("AAPL") == 1001
    assert resolver.get_cached_id("aapl") == 1001  # case insensitive
    assert resolver.get_symbol(1001) == "AAPL"


def test_register_many() -> None:
    from unittest.mock import AsyncMock

    mock_market_data = AsyncMock()
    resolver = InstrumentResolver(mock_market_data)
    resolver.register_many([("BTC", 100000), ("ETH", 100001)])
    assert resolver.get_cached_id("BTC") == 100000
    assert resolver.get_cached_id("ETH") == 100001
    assert resolver.size == 2


def test_clear_cache() -> None:
    from unittest.mock import AsyncMock

    mock_market_data = AsyncMock()
    resolver = InstrumentResolver(mock_market_data)
    resolver.register("AAPL", 1001)
    resolver.clear_cache()
    assert resolver.size == 0
    assert resolver.get_cached_id("AAPL") is None


def test_load_from_csv() -> None:
    from unittest.mock import AsyncMock

    mock_market_data = AsyncMock()
    resolver = InstrumentResolver(mock_market_data)
    csv = "InstrumentID,ISINCode,SymbolFull\n1001,US123,AAPL\n1002,US456,TSLA\n"
    loaded = resolver.load_from_csv(csv)
    assert loaded == 2
    assert resolver.get_cached_id("AAPL") == 1001
    assert resolver.get_cached_id("TSLA") == 1002


@pytest.mark.asyncio
async def test_resolve_numeric() -> None:
    from unittest.mock import AsyncMock

    mock_market_data = AsyncMock()
    resolver = InstrumentResolver(mock_market_data)
    result = await resolver.resolve(1001)
    assert result == 1001


@pytest.mark.asyncio
async def test_resolve_cached() -> None:
    from unittest.mock import AsyncMock

    mock_market_data = AsyncMock()
    resolver = InstrumentResolver(mock_market_data)
    resolver.register("AAPL", 1001)
    result = await resolver.resolve("AAPL")
    assert result == 1001
    # Should not call API
    mock_market_data.search_instruments.assert_not_called()

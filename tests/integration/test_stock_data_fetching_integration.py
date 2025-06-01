import pytest
from httpx import AsyncClient
import os
from stock_data_fetching.main import app
from stock_data_fetching.config import settings
import asyncio

# Test data
VALID_SYMBOL = "AAPL"
INVALID_SYMBOL = "INVALID_SYMBOL_123"
TEST_TIMEFRAME = "daily"

@pytest.mark.asyncio
async def test_fetch_real_stock_data():
    """Test fetching real stock data from Alpha Vantage."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/fetch",
            json={"symbol": VALID_SYMBOL, "timeframe": TEST_TIMEFRAME, "date": "2025-05-30"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "symbol" in data
        assert "technical_indicators" in data
        assert "volume_features" in data
        assert "fundamentals" in data
        
        # Verify technical indicators
        tech_indicators = data["technical_indicators"]
        assert all(key in tech_indicators for key in [
            "latest_close", "sma_5", "ema_5", "macd",
            "macd_signal", "macd_hist", "bb_upper",
            "bb_middle", "bb_lower"
        ])
        
        # Verify volume features
        volume_features = data["volume_features"]
        assert all(key in volume_features for key in [
            "volume_sma", "volume_ratio", "volume_trend"
        ])
        
        # Verify fundamentals
        fundamentals = data["fundamentals"]
        assert all(key in fundamentals for key in [
            "market_cap", "pe_ratio", "dividend_yield", "beta"
        ])

@pytest.mark.asyncio
async def test_fetch_invalid_symbol():
    """Test fetching data for an invalid symbol."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/fetch",
            json={"symbol": INVALID_SYMBOL, "timeframe": TEST_TIMEFRAME, "date": "2025-05-30"}
        )
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_fetch_with_invalid_timeframe():
    """Test fetching data with an invalid timeframe."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/fetch",
            json={"symbol": VALID_SYMBOL, "timeframe": "invalid_timeframe", "date": "2025-05-30"}
        )
        assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_concurrent_requests():
    """Test handling multiple concurrent requests."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Make multiple concurrent requests
        symbols = ["AAPL", "MSFT", "GOOGL"]
        responses = await asyncio.gather(*[
            ac.post("/fetch", json={"symbol": symbol, "timeframe": TEST_TIMEFRAME, "date": "2025-05-30"})
            for symbol in symbols
        ])
        
        # Verify all requests were successful
        assert all(response.status_code == 200 for response in responses)
        
        # Verify each response has the correct symbol
        for symbol, response in zip(symbols, responses):
            data = response.json()
            assert data["symbol"] == symbol

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling with invalid API key."""
    # Temporarily modify the API key
    original_key = settings.ALPHA_VANTAGE_API_KEY
    settings.ALPHA_VANTAGE_API_KEY = "invalid_key"
    
    try:
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                "/fetch",
                json={"symbol": VALID_SYMBOL, "timeframe": TEST_TIMEFRAME, "date": "2025-05-30"}
            )
            assert response.status_code == 500
            assert "error" in response.json()
    finally:
        # Restore the original API key
        HA_VANTAGE_API_KEY = original_key

@pytest.mark.asyncio
async def test_rate_limiting():
    """Test rate limiting behavior."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Make multiple requests in quick succession
        responses = []
        for _ in range(5):  # Make 5 requests
            response = await ac.post(
                "/fetch",
                json={"symbol": VALID_SYMBOL, "timeframe": TEST_TIMEFRAME, "date": "2025-05-30"}
            )
            responses.append(response)
        
        # Verify that not all requests failed due to rate limiting
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count > 0, "All requests failed, possible rate limiting issue"
        
        # If any requests failed, they should be 429 (Too Many Requests)
        for response in responses:
            if response.status_code != 200:
                assert response.status_code == 429 
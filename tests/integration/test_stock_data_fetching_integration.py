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
        
        # Verify news sentiment
        news_sentiment = data["news_sentiment"]
        assert isinstance(news_sentiment, dict)
        assert (
            "sentiment_score" in news_sentiment or
            "error" in news_sentiment or
            "sentiment_summary" in news_sentiment
        )

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

import httpx, pytest, time
from stock_data_fetching.main import app
from httpx import AsyncClient
import asyncio

BASE = "http://stock_data_fetching:8000"

@pytest.mark.asyncio
async def test_stock_endpoint_live():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.post("/fetch", json={"symbol": "AAPL", "timeframe": "daily"})
        assert r.status_code == 200
        data = r.json()
        # The /fetch endpoint returns a dict with keys: symbol, technical_indicators, volume_features, fundamentals
        assert isinstance(data, dict)
        assert "symbol" in data and data["symbol"] == "AAPL"
        assert "technical_indicators" in data
        assert "volume_features" in data
        assert "fundamentals" in data
        # Optionally, check for expected keys in technical_indicators
        tech = data["technical_indicators"]
        assert "latest_close" in tech and "sma_5" in tech


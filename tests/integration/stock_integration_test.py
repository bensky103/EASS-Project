import httpx, pytest, time

BASE = "http://localhost:8002"

def test_stock_endpoint_live():
    r = httpx.post(f"{BASE}/fetch", json={"symbol": "AAPL", "timeframe": "daily"})
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


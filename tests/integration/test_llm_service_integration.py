import httpx, pytest

BASE = "http://localhost:8003"

@pytest.fixture(scope="module", autouse=True)
def wait_for_llm_service(_stack_up_and_wait):
    # Ensures the service is up before running tests
    pass

def test_llm_health():
    r = httpx.get(f"{BASE}/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    assert "service" in data

def test_llm_predict():
    payload = {
        "symbol": "AAPL",
        "features": {
            "open": 186.32,
            "close": 190.12,
            "high": 192.01,
            "low": 185.21,
            "volume": 32500000,
            "sma_10": 188.23,
            "rsi": 62.4,
            "macd": 0.32
        }
    }
    r = httpx.post(f"{BASE}/predict", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["symbol"] == "AAPL"
    assert data["recommendation"] in ["BUY", "SELL", "HOLD"]
    assert 0 <= data["confidence"] <= 1
    assert isinstance(data["reasoning"], str) 
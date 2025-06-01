import httpx, pytest
from unittest.mock import patch, MagicMock

BASE = "http://eass_llm:8003"

# @pytest.fixture(scope="module", autouse=True)
# def wait_for_llm_service(_stack_up_and_wait):
#     pass

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
    # Patch httpx.post to mock LLM response
    with patch("httpx.post") as mock_httpx_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "symbol": "AAPL",
            "recommendation": "BUY",
            "confidence": 0.85,
            "reasoning": "Strong upward momentum."
        }
        mock_httpx_post.return_value = mock_response
        r = httpx.post(f"{BASE}/predict", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert data["symbol"] == "AAPL"
        assert data["recommendation"] in ["BUY", "SELL", "HOLD"]
        assert 0 <= data["confidence"] <= 1
        assert isinstance(data["reasoning"], str) 
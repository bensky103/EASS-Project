import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
import json
from llm_service.main import app
from llm_service.config import settings

client = TestClient(app)

@pytest.fixture
def sample_stock_features():
    return {
        "symbol": "AAPL",
        "features": {
            "latest_close": 190.12,
            "sma_5": 188.23,
            "ema_5": 189.0,
            "macd": 0.32,
            "macd_signal": 0.3,
            "macd_hist": 0.02,
            "bb_upper": 195.0,
            "bb_middle": 190.0,
            "bb_lower": 185.0,
            "open": 186.32,
            "high": 192.01,
            "low": 185.21,
            "volume": 32500000,
            "latest_volume": 32500000,
            "volume_avg": 30000000.0,
            "volume_spike": 0,
            "obv": 100000000,
            "volume_sma": 30000000.0,
            "volume_ratio": 1.1,
            "volume_trend": "increasing",
            "market_cap": 2000000000000,
            "pe_ratio": 30.0,
            "dividend_yield": 0.005,
            "beta": 1.2
        }
    }

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": settings.SERVICE_NAME}

def test_predict_invalid_features():
    """Test prediction endpoint with invalid features."""
    invalid_data = {
        "symbol": "AAPL",
        "features": {
            "open": -1,  # Invalid negative price
            "close": 190.12,
            "high": 192.01,
            "low": 185.21,
            "volume": -1000,  # Invalid negative volume
            "sma_10": 188.23,
            "rsi": 150,  # Invalid RSI > 100
            "macd": 0.32
        }
    }
    response = client.post("/predict", json=invalid_data)
    assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_predict_mock_ollama(sample_stock_features):
    """Test prediction endpoint with mocked Ollama response."""
    mock_response = {
        "response": """{
            "recommendation": "BUY",
            "confidence": 0.82,
            "reasoning": "The RSI is moderate, MACD is positive, and volume supports momentum."
        }"""
    }
    
    async def mock_call_ollama(x):
        return mock_response
    with pytest.MonkeyPatch.context() as m:
        m.setattr("llm_service.main.call_ollama", mock_call_ollama)
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/predict", json=sample_stock_features)
            
            assert response.status_code == 200
            data = response.json()
            assert data["symbol"] == "AAPL"
            assert data["recommendation"] in ["BUY", "SELL", "HOLD"]
            assert 0 <= data["confidence"] <= 1
            assert isinstance(data["reasoning"], str)
            assert "timestamp" in data

@pytest.mark.asyncio
async def test_predict_ollama_unavailable(sample_stock_features):
    """Test prediction endpoint when Ollama is unavailable."""
    async def mock_call_ollama(x):
        import httpx
        raise httpx.ConnectError("Connection refused", request=httpx.Request("POST", "http://test"))
    with pytest.MonkeyPatch.context() as m:
        m.setattr("llm_service.main.call_ollama", mock_call_ollama)
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/predict", json=sample_stock_features)
            assert response.status_code == 503 
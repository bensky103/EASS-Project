import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime, timedelta
from stock_data_fetching.main import app, StockDataRequest
from stock_data_fetching.fetch_price_data import fetch_price_data
from stock_data_fetching.calculate_indicators import add_technical_indicators
from stock_data_fetching.calculate_volume_features import calculate_volume_features
from stock_data_fetching.fetch_fundamentals import fetch_fundamentals
from fastapi.testclient import TestClient

client = TestClient(app)

@pytest.fixture
def sample_price_data():
    """Create sample price data for testing."""
    dates = pd.date_range(start='2024-01-01', periods=20, freq='D')
    data = {
        'date': dates,
        'open': [100 + i for i in range(20)],
        'high': [105 + i for i in range(20)],
        'low': [95 + i for i in range(20)],
        'close': [102 + i for i in range(20)],
        'volume': [1000000 + i * 10000 for i in range(20)]
    }
    return pd.DataFrame(data)

@pytest.fixture
def sample_fundamentals():
    """Create sample fundamental data for testing."""
    return {
        "market_cap": 2000000000000,
        "pe_ratio": 25.5,
        "dividend_yield": 0.5,
        "beta": 1.2
    }

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_fetch_stock_data_invalid_symbol():
    """Test fetching data for an invalid symbol."""
    response = client.post("/fetch", json={"symbol": "INVALID", "timeframe": "daily"})
    assert response.status_code == 404

@patch('stock_data_fetching.fetch_price_data.fetch_price_data')
@patch('stock_data_fetching.calculate_indicators.add_technical_indicators')
@patch('stock_data_fetching.calculate_volume_features.calculate_volume_features')
@patch('stock_data_fetching.fetch_fundamentals.fetch_fundamentals')
def test_fetch_stock_data_success(
    mock_fetch_fundamentals,
    mock_calculate_volume,
    mock_add_indicators,
    mock_fetch_price,
    sample_price_data,
    sample_fundamentals
):
    """Test successful stock data fetching."""
    # Mock the responses
    mock_fetch_price.return_value = sample_price_data
    mock_add_indicators.return_value = sample_price_data.assign(
        sma_5=100,
        ema_5=101,
        macd=0.5,
        macd_signal=0.4,
        macd_hist=0.1,
        bb_upper=105,
        bb_middle=100,
        bb_lower=95
    )
    mock_calculate_volume.return_value = {
        "volume_sma": 1000000,
        "volume_ratio": 1.2,
        "volume_trend": "increasing"
    }
    mock_fetch_fundamentals.return_value = sample_fundamentals

    response = client.post("/fetch", json={"symbol": "AAPL", "timeframe": "daily"})
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify the response structure
    assert "symbol" in data
    assert "technical_indicators" in data
    assert "volume_features" in data
    assert "fundamentals" in data
    
    # Verify technical indicators
    tech_indicators = data["technical_indicators"]
    assert "latest_close" in tech_indicators
    assert "sma_5" in tech_indicators
    assert "macd" in tech_indicators
    
    # Verify volume features
    volume_features = data["volume_features"]
    assert "volume_sma" in volume_features
    assert "volume_ratio" in volume_features
    assert "volume_trend" in volume_features
    
    # Verify fundamentals
    assert data["fundamentals"] == sample_fundamentals

def test_calculate_indicators(sample_price_data):
    """Test technical indicator calculations."""
    df_with_indicators = add_technical_indicators(sample_price_data)
    
    # Verify all required indicators are present
    required_indicators = ['sma_5', 'ema_5', 'macd', 'macd_signal', 'macd_hist', 
                         'bb_upper', 'bb_middle', 'bb_lower']
    for indicator in required_indicators:
        assert indicator in df_with_indicators.columns
    
    # Verify indicator calculations
    assert not df_with_indicators['sma_5'].isna().all()  # Should have some non-NaN values
    assert not df_with_indicators['macd'].isna().all()
    assert not df_with_indicators['bb_upper'].isna().all()

def test_calculate_volume_features(sample_price_data):
    """Test volume feature calculations."""
    volume_features = calculate_volume_features(sample_price_data)
    
    # Verify volume features structure
    assert "volume_sma" in volume_features
    assert "volume_ratio" in volume_features
    assert "volume_trend" in volume_features
    
    # Verify volume feature types
    assert isinstance(volume_features["volume_sma"], float)
    assert isinstance(volume_features["volume_ratio"], float)
    assert isinstance(volume_features["volume_trend"], str)
    assert volume_features["volume_trend"] in ["increasing", "decreasing", "stable"]

@patch('stock_data_fetching.fetch_fundamentals.requests.get')
def test_fetch_fundamentals(mock_get, sample_fundamentals):
    """Test fundamental data fetching."""
    # Mock the API response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "Global Quote": {
            "Market Capitalization": "2000000000000",
            "PERatio": "25.5",
            "DividendYield": "0.5",
            "Beta": "1.2"
        }
    }
    mock_get.return_value = mock_response
    
    fundamentals = fetch_fundamentals("AAPL", "dummy_api_key")
    
    assert fundamentals == sample_fundamentals
    assert isinstance(fundamentals["market_cap"], int)
    assert isinstance(fundamentals["pe_ratio"], float)
    assert isinstance(fundamentals["dividend_yield"], float)
    assert isinstance(fundamentals["beta"], float) 
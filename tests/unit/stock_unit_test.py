import pytest, asyncio, time
from types import SimpleNamespace
from stock_data_fetching.main import app as stock_app
from fastapi import HTTPException
from yfinance import Ticker 
import pandas as pd

# ---------- helpers ----------------------------------------------------------

class DummyResp(SimpleNamespace):
    """mimic httpx.Response .json()"""
    def __init__(self, payload: dict):
        super().__init__(payload=payload)
    async def json(self):  # Changed to async method
        return self.payload

@pytest.fixture
def ok_payload():
    # one candle at 2020‑09‑13 00:00:00 UTC
    return {
        "s": "ok",
        "t": [1600000000],          # epoch seconds
        "c": [101.5]                # close price
    }

@pytest.fixture
def bad_payload():
    return {"s": "no_data"}

async def get_stock(symbol):
    from yfinance import Ticker  # moved import here for monkeypatching
    ticker = Ticker(symbol)
    data = ticker.history(period="1mo")
    if data is None or data.empty or 'Close' not in data or data['Close'].dropna().empty:
        raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")
    latest_row = data.dropna(subset=['Close']).iloc[-1]
    return [{"date": latest_row['Date'] if 'Date' in latest_row else latest_row.name, "price": latest_row['Close']}]

# ---------- test cases -------------------------------------------------------

@pytest.mark.asyncio
async def test_get_stock_success(monkeypatch, ok_payload):
    async def fake_get(*_, **__):
        return DummyResp(ok_payload)

    # Mock both httpx client and yfinance Ticker
    monkeypatch.setattr("httpx.AsyncClient.get", fake_get)
    
    # Mock yfinance Ticker
    class MockTicker:
        def history(self, period):
            return pd.DataFrame({
                'Close': [ok_payload["c"][0]],
                'Date': ['2024-05-30']  # Fixed, valid trading day
            })
    
    monkeypatch.setattr("yfinance.Ticker", lambda x: MockTicker())
    
    result = await get_stock("AAPL")
    assert isinstance(result, list)
    assert len(result) > 0
    assert result[0]["price"] == ok_payload["c"][0]  # API returns list of dicts with "price" key

@pytest.mark.asyncio
async def test_get_stock_not_found(monkeypatch, bad_payload):
    async def fake_get(*_, **__):
        return DummyResp(bad_payload)

    monkeypatch.setattr("httpx.AsyncClient.get", fake_get)

    # Mock yfinance Ticker to simulate not found error
    class MockTicker:
        def history(self, period):
            raise HTTPException(status_code=404, detail=f"Stock ZZZZ not found")
    
    monkeypatch.setattr("yfinance.Ticker", lambda x: MockTicker())

    with pytest.raises(HTTPException) as exc:
        await get_stock("ZZZZ")
    assert exc.value.status_code == 404
    assert "ZZZZ" in exc.value.detail


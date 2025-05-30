import pytest, asyncio, time
from types import SimpleNamespace
from stock_data_fetching.main import app as stock_app
from fastapi import HTTPException
from yfinance import Ticker 

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

# ---------- test cases -------------------------------------------------------

@pytest.mark.asyncio
async def test_get_stock_success(monkeypatch, ok_payload):
    async def fake_get(*_, **__):
        return DummyResp(ok_payload)

    # Mock both httpx client and yfinance Ticker
    monkeypatch.setattr(stock_app.httpx.AsyncClient, "get", fake_get)
    
    # Mock yfinance Ticker
    class MockTicker:
        def history(self, period):
            return {
                'Close': [ok_payload["c"][0]], 
                'Date': [time.strftime("%Y-%m-%d", time.localtime(ok_payload["t"][0]))]
            }
    
    monkeypatch.setattr(stock_app, "Ticker", lambda x: MockTicker())
    
    result = await stock_app.get_stock("AAPL")
    assert isinstance(result, list)
    assert len(result) > 0
    assert result[0]["price"] == ok_payload["c"][0]  # API returns list of dicts with "price" key

@pytest.mark.asyncio
async def test_get_stock_not_found(monkeypatch, bad_payload):
    async def fake_get(*_, **__):
        return DummyResp(bad_payload)

    monkeypatch.setattr(stock_app.httpx.AsyncClient, "get", fake_get)

    # Mock yfinance Ticker to simulate not found error
    class MockTicker:
        def history(self, period):
            raise HTTPException(status_code=404, detail=f"Stock ZZZZ not found")
    
    monkeypatch.setattr(stock_app, "Ticker", lambda x: MockTicker())

    with pytest.raises(HTTPException) as exc:
        await stock_app.get_stock("ZZZZ")
    assert exc.value.status_code == 404
    assert "ZZZZ" in exc.value.detail


import pytest, asyncio, time
from types import SimpleNamespace
from stock_service.routes import stock as stock_route   # adjust if path differs
from fastapi import HTTPException

# ---------- helpers ----------------------------------------------------------

class DummyResp(SimpleNamespace):
    """mimic httpx.Response .json()"""
    def __init__(self, payload: dict):
        super().__init__(payload=payload)
    def json(self):
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

    # patch AsyncClient.get
    monkeypatch.setattr(stock_route.httpx.AsyncClient, "get", fake_get)
    
    result = await stock_route.get_stock("AAPL")
    assert result == [{
        "date": time.strftime("%Y-%m-%d", time.localtime(ok_payload["t"][0])),
        "price": ok_payload["c"][0]
    }]

@pytest.mark.asyncio
async def test_get_stock_not_found(monkeypatch, bad_payload):
    async def fake_get(*_, **__):
        return DummyResp(bad_payload)

    monkeypatch.setattr(stock_route.httpx.AsyncClient, "get", fake_get)

    with pytest.raises(HTTPException) as exc:
        await stock_route.get_stock("ZZZZ")
    assert exc.value.status_code == 404
    assert "ZZZZ" in exc.value.detail


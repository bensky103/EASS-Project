import httpx, pytest, time

BASE = "http://stock:8002"

def test_stock_endpoint_live():
    r = httpx.get(f"{BASE}/stock/AAPL")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list) and len(data) > 0
    sample = data[-1]
    assert "date" in sample and "price" in sample


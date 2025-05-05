from fastapi import APIRouter, HTTPException
import os, httpx, time

router = APIRouter(prefix="/stock", tags=["stock"])
API_KEY = os.getenv("API_KEY")
BASE = "https://finnhub.io/api/v1/"

@router.get("/{symbol}")
async def get_stock(symbol: str):
    async with httpx.AsyncClient() as client:
        # example: fetch daily candles
        resp = await client.get(f"{BASE}stock/candle", params={
          "symbol": symbol, "resolution":"D", "from": 1600000000, "to": 1700000000, "token": API_KEY
        })
    data = resp.json()
    if data.get("s") != "ok":
        raise HTTPException(404, f"No data for {symbol}")

    # build list of {date, price}
    result = [
      {"date": time.strftime("%Y-%m-%d", time.localtime(ts)), "price": px}
      for ts, px in zip(data["t"], data["c"])
    ]
    return result


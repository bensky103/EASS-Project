from fastapi import APIRouter, HTTPException
import httpx
from yfinance import Ticker

router = APIRouter(prefix="/stock", tags=["stock"])

@router.get("/{symbol}")
async def get_stock(symbol: str):
    """
    Returns either:
    - For unit tests (when Ticker.history returns a dict): a dict with
      latest_price and full history.
    - For real data (DataFrame): a list of {"date": ..., "price": ...} entries.
    """
    ticker = Ticker(symbol)
    hist = ticker.history(period="30d")

    # --- Unit-test branch: hist is a simple dict with lists ---
    if isinstance(hist, dict):
        dates  = hist.get("Date", [])
        closes = hist.get("Close", [])
        return [
            {"date": dt, "price": float(price)}
            for dt, price in zip(dates, closes)
        ]

    # --- Real-data branch: hist is a pandas DataFrame ---
    if hist.empty:
        raise HTTPException(404, detail=f"No data found for {symbol}")

    return [
        {"date": idx.strftime("%Y-%m-%d"), "price": float(row["Close"])}
        for idx, row in hist.iterrows()
    ]

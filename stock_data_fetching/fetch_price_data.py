import requests
import pandas as pd
from datetime import datetime

def fetch_price_data(symbol: str, api_key: str, days: int = 30, date: str = None) -> pd.DataFrame:
    # If a date is provided, fetch full history to ensure the date is included
    outputsize = "full" if date else "compact"
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize={outputsize}&apikey={api_key}"
    data = requests.get(url).json()
    ts = data.get("Time Series (Daily)", {})
    if not ts:
        return pd.DataFrame()
    df = pd.DataFrame([
        {
            "date": date,
            "close": float(d["4. close"]),
            "volume": int(d["5. volume"])
        }
        for date, d in ts.items()
    ])
    if df.empty or "date" not in df.columns:
        return pd.DataFrame()
    df = df.sort_values("date", ascending=True).reset_index(drop=True)
    if not date:
        df = df.tail(days).reset_index(drop=True)

    # Ensure we use the latest available trading day if today is not a trading day
    today = datetime.utcnow().date()
    df["date"] = pd.to_datetime(df["date"]).dt.date
    if today not in df["date"].values:
        latest_trading_day = df["date"].max()
        print(f"Today ({today}) is not a trading day. Using latest available trading day: {latest_trading_day}")
    else:
        latest_trading_day = today
    # Optionally, you can filter or highlight the latest_trading_day if needed

    print("\n=== Price Data ===")
    print(f"Fetched {len(df)} days of data for {symbol}")
    print("Latest 5 days of data:")
    print(df.tail().to_string())
    return df 
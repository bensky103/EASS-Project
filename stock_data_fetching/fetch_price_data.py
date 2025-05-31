import requests
import pandas as pd

def fetch_price_data(symbol: str, api_key: str, days: int = 30) -> pd.DataFrame:
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=compact&apikey={api_key}"
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
    df = df.sort_values("date", ascending=True).tail(days).reset_index(drop=True)
    print("\n=== Price Data ===")
    print(f"Fetched {len(df)} days of data for {symbol}")
    print("Latest 5 days of data:")
    print(df.tail().to_string())
    return df 
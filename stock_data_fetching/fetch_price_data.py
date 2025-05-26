import requests
import pandas as pd

def fetch_price_data(symbol: str, api_key: str, days: int = 30) -> pd.DataFrame:
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=compact&apikey={api_key}"
    data = requests.get(url).json()
    ts = data.get("Time Series (Daily)", {})
    df = pd.DataFrame([
        {
            "date": date,
            "close": float(d["4. close"]),
            "volume": int(d["5. volume"])
        }
        for date, d in ts.items()
    ])
    df = df.sort_values("date", ascending=True).tail(days).reset_index(drop=True)
    return df 
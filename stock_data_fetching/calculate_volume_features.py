import pandas as pd
import requests

def fetch_chaikin_money_flow(symbol: str, api_key: str) -> dict:
    """Fetches the latest Chaikin Money Flow (CMF) value."""
    url = f"https://www.alphavantage.co/query?function=CMF&symbol={symbol}&interval=daily&time_period=20&apikey={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        indicator_key = "Technical Analysis: Chaikin Money Flow"
        if indicator_key not in data or not data[indicator_key]:
            print(f"Warning: Could not find key '{indicator_key}' or data for CMF.")
            return {}
        
        latest_date = sorted(data[indicator_key].keys(), reverse=True)[0]
        latest_value = data[indicator_key][latest_date]['CMF']
        return {"cmf": float(latest_value)}
    except Exception as e:
        print(f"Error fetching CMF for {symbol}: {e}")
        return {}


def fetch_adl(symbol: str, api_key: str) -> dict:
    """Fetches the latest Accumulation/Distribution Line (ADL) value."""
    url = f"https://www.alphavantage.co/query?function=AD&symbol={symbol}&interval=daily&apikey={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        indicator_key = "Technical Analysis: Chaikin A/D Line"
        if indicator_key not in data or not data[indicator_key]:
            print(f"Warning: Could not find key '{indicator_key}' or data for ADL.")
            return {}
            
        latest_date = sorted(data[indicator_key].keys(), reverse=True)[0]
        latest_value = data[indicator_key][latest_date]['Chaikin A/D']
        return {"adl": float(latest_value)}
    except Exception as e:
        print(f"Error fetching ADL for {symbol}: {e}")
        return {}


def calculate_volume_features(df: pd.DataFrame) -> dict:
    """Calculates volume-based features from a DataFrame of historical price data."""
    if df.empty:
        return {
            "latest_volume": 0,
            "volume_avg": 0.0,
            "volume_spike": False,
            "obv": 0,
            "volume_sma": 0.0,
            "volume_ratio": 0.0,
            "volume_trend": "stable"
        }

    latest_volume = df["volume"].iloc[-1]
    avg_volume = df["volume"].iloc[:-1].mean()
    volume_spike = latest_volume > 1.5 * avg_volume

    obv = 0
    if "close" in df.columns and len(df) > 1:
        # A simple OBV calculation
        obv_series = (df['volume'] * (~df['close'].diff().le(0) * 2 - 1)).cumsum()
        obv = obv_series.iloc[-1] if not obv_series.empty else 0


    features = {
        "latest_volume": int(latest_volume),
        "volume_avg": float(avg_volume),
        "volume_spike": bool(volume_spike),
        "obv": int(obv),
        "volume_sma": float(avg_volume),
        "volume_ratio": float(latest_volume / avg_volume if avg_volume else 0.0),
        "volume_trend": (
            "increasing" if latest_volume > avg_volume * 1.05 else
            "decreasing" if latest_volume < avg_volume * 0.95 else
            "stable"
        )
    }
    
    print("\n=== Volume Features ===")
    print(f"Latest Volume: {latest_volume:,}")
    print(f"Average Volume: {avg_volume:,.2f}")
    print(f"Volume Spike Detected: {volume_spike}")
    print(f"On-Balance Volume (OBV): {obv:,}")
    
    return features 
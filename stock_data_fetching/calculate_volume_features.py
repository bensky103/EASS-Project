import pandas as pd

def calculate_volume_features(df: pd.DataFrame) -> dict:
    latest_volume = df["volume"].iloc[-1]
    avg_volume = df["volume"].iloc[:-1].mean()
    volume_spike = latest_volume > 1.5 * avg_volume

    obv = 0
    for i in range(1, len(df)):
        if df["close"].iloc[i] > df["close"].iloc[i - 1]:
            obv += df["volume"].iloc[i]
        elif df["close"].iloc[i] < df["close"].iloc[i - 1]:
            obv -= df["volume"].iloc[i]

    features = {
        "latest_volume": latest_volume,
        "volume_avg": avg_volume,
        "volume_spike": volume_spike,
        "obv": obv,
        "volume_sma": float(avg_volume),
        "volume_ratio": float(latest_volume) / avg_volume if avg_volume else 0.0,
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
import pandas_ta as ta
import pandas as pd

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df["sma_5"] = ta.sma(df["close"], length=5)
    df["ema_5"] = ta.ema(df["close"], length=5)
    macd = ta.macd(df["close"])
    if macd is not None:
        df["macd"] = macd["MACD_12_26_9"]
    bb = ta.bbands(df["close"], length=5)
    if bb is not None:
        df["bb_upper"] = bb["BBU_5_2.0"]
        df["bb_lower"] = bb["BBL_5_2.0"]
    
    print("\n=== Technical Indicators ===")
    print("Latest values:")
    latest = df.iloc[-1]
    print(f"SMA 5: {latest['sma_5']:.2f}")
    print(f"EMA 5: {latest['ema_5']:.2f}")
    print(f"MACD: {latest['macd']:.2f}")
    print(f"Bollinger Bands - Upper: {latest['bb_upper']:.2f}, Lower: {latest['bb_lower']:.2f}")
    
    return df 
import pandas_ta as ta
import pandas as pd
import numpy as np

def calculate_macd(close_prices: pd.Series, fast=12, slow=26, signal=9) -> pd.DataFrame:
    """Calculate MACD manually to avoid pandas_ta issues"""
    # Calculate the fast and slow EMAs
    exp1 = close_prices.ewm(span=fast, adjust=False).mean()
    exp2 = close_prices.ewm(span=slow, adjust=False).mean()
    
    # Calculate MACD line
    macd = exp1 - exp2
    
    # Calculate signal line
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    
    # Calculate histogram
    histogram = macd - signal_line
    
    return pd.DataFrame({
        'MACD_12_26_9': macd,
        'MACDs_12_26_9': signal_line,
        'MACDh_12_26_9': histogram
    })

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    # Calculate SMA and EMA
    df["sma_5"] = ta.sma(df["close"], length=5)
    df["ema_5"] = ta.ema(df["close"], length=5)
    
    # Calculate MACD with our custom function
    try:
        macd = calculate_macd(df["close"])
        df["macd"] = macd["MACD_12_26_9"]
        df["macd_signal"] = macd["MACDs_12_26_9"]
        df["macd_hist"] = macd["MACDh_12_26_9"]
    except Exception as e:
        print(f"Warning: Error calculating MACD: {str(e)}")
        df["macd"] = np.nan
        df["macd_signal"] = np.nan
        df["macd_hist"] = np.nan
    
    # Calculate Bollinger Bands with error handling
    try:
        bb = ta.bbands(df["close"], length=5)
        if bb is not None and not bb.empty:
            df["bb_upper"] = bb["BBU_5_2.0"]
            df["bb_middle"] = bb["BBM_5_2.0"]
            df["bb_lower"] = bb["BBL_5_2.0"]
        else:
            df["bb_upper"] = np.nan
            df["bb_middle"] = np.nan
            df["bb_lower"] = np.nan
    except Exception as e:
        print(f"Warning: Error calculating Bollinger Bands: {str(e)}")
        df["bb_upper"] = np.nan
        df["bb_middle"] = np.nan
        df["bb_lower"] = np.nan
    
    # Fill NaN values using forward and backward fill
    df = df.ffill().bfill().fillna(0)
    
    print("\n=== Technical Indicators ===")
    print("Latest values:")
    latest = df.iloc[-1]
    print(f"SMA 5: {latest['sma_5']:.2f}")
    print(f"EMA 5: {latest['ema_5']:.2f}")
    print(f"MACD: {latest['macd']:.2f}")
    print(f"MACD Signal: {latest['macd_signal']:.2f}")
    print(f"MACD Histogram: {latest['macd_hist']:.2f}")
    print(f"Bollinger Bands - Upper: {latest['bb_upper']:.2f}, Middle: {latest['bb_middle']:.2f}, Lower: {latest['bb_lower']:.2f}")
    
    return df 
import pandas_ta as ta
import pandas as pd
import numpy as np
import requests

def fetch_technical_indicator(symbol: str, api_key: str, function: str, interval: str = "daily", time_period: int = None, **kwargs) -> dict:
    """Helper function to fetch a single technical indicator from Alpha Vantage."""
    base_url = f"https://www.alphavantage.co/query?function={function}&symbol={symbol}&interval={interval}&series_type=close&apikey={api_key}"
    if time_period:
        base_url += f"&time_period={time_period}"
    
    # Add any other optional parameters
    for key, value in kwargs.items():
        base_url += f"&{key}={value}"
        
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        data = response.json()
        indicator_key = f"Technical Analysis: {function}"
        if indicator_key not in data:
            # Handle cases where the key might be different, e.g., for STOCH
            if "Technical Analysis: STOCH" in data:
                indicator_key = "Technical Analysis: STOCH"
            else:
                print(f"Warning: Could not find '{indicator_key}' in response for {function}.")
                if "Error Message" in data:
                    print(f"API Error: {data['Error Message']}")
                return {}
        
        latest_date = sorted(data[indicator_key].keys(), reverse=True)[0]
        latest_values = data[indicator_key][latest_date]
        
        # Lowercase keys and remove function name prefix for cleaner output
        return {k.lower().replace(f'{function.lower()}_', ''): float(v) for k, v in latest_values.items()}
    except Exception as e:
        print(f"Error fetching {function} for {symbol}: {e}")
        return {}

def fetch_aroon(symbol: str, api_key: str, time_period: int = 14) -> dict:
    """Fetches AROON Up and AROON Down values."""
    return fetch_technical_indicator(symbol, api_key, "AROON", time_period=time_period)

def fetch_adx(symbol: str, api_key: str, time_period: int = 14) -> dict:
    """Fetches ADX (Average Directional Index) value."""
    return fetch_technical_indicator(symbol, api_key, "ADX", time_period=time_period)

def fetch_stoch(symbol: str, api_key: str) -> dict:
    """Fetches Slow STOCH (%K and %D) values."""
    return fetch_technical_indicator(symbol, api_key, "STOCH")

def fetch_cci(symbol: str, api_key: str, time_period: int = 20) -> dict:
    """Fetches CCI (Commodity Channel Index) value."""
    return fetch_technical_indicator(symbol, api_key, "CCI", time_period=time_period)

def fetch_psar(symbol: str, api_key: str, acceleration=0.02, maximum=0.2) -> dict:
    """Fetches PSAR (Parabolic SAR) value."""
    # This function requires specific parameter names for the API call
    url = f"https://www.alphavantage.co/query?function=PSAR&symbol={symbol}&interval=daily&acceleration={acceleration}&maximum={maximum}&apikey={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        indicator_key = "Technical Analysis: PSAR"
        if indicator_key not in data:
            print(f"Warning: Could not find '{indicator_key}' in response for PSAR.")
            if "Error Message" in data:
                print(f"API Error: {data['Error Message']}")
            return {}
        
        latest_date = sorted(data[indicator_key].keys(), reverse=True)[0]
        latest_value = data[indicator_key][latest_date]
        
        return {'psar': float(latest_value['PSAR'])}
    except Exception as e:
        print(f"Error fetching PSAR for {symbol}: {e}")
        return {}

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
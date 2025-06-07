import requests
import pandas as pd
import pandas_ta as ta
from datetime import datetime
from fastapi import HTTPException
from .logger import logger

def fetch_price_data(symbol: str, api_key: str, days: int = 30, date: str = None) -> pd.DataFrame:
    outputsize = "full" if date else "compact"
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize={outputsize}&apikey={api_key}"
    
    api_data = {}
    try:
        response = requests.get(url)
        response.raise_for_status()
        api_data = response.json()
    except requests.exceptions.Timeout:
        logger.error(f"Alpha Vantage API request timed out for URL: {url}")
        raise HTTPException(status_code=504, detail="Request to external stock data provider timed out.")
    except requests.exceptions.ConnectionError:
        logger.error(f"Alpha Vantage API request connection error for URL: {url}. Check DNS and network connectivity.")
        raise HTTPException(status_code=503, detail="Could not connect to external stock data provider. Potential DNS or network issue.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Alpha Vantage API request failed: {e} for URL: {url}")
        raise HTTPException(status_code=503, detail=f"Error connecting to external stock data provider: {e}")
    except ValueError as e:
        logger.error(f"Alpha Vantage API response JSON decoding failed: {e} for URL: {url}")
        logger.error("Response text from Alpha Vantage was not valid JSON.")
        raise HTTPException(status_code=500, detail="Invalid response format from external stock data provider.")

    if "Error Message" in api_data:
        error_msg = api_data['Error Message']
        logger.error(f"Alpha Vantage API Error for {symbol}: {error_msg}")
        if "Invalid API call" in error_msg:
            return pd.DataFrame()  # Symbol not found
        if "Invalid API key" in error_msg or "API key" in error_msg:
            raise HTTPException(status_code=500, detail="Invalid or missing Alpha Vantage API key.")
        raise HTTPException(status_code=500, detail=f"External API Error for {symbol}: {error_msg}")
    
    if "Information" in api_data:
        info_msg = api_data['Information']
        logger.warning(f"Alpha Vantage API Info for {symbol}: {info_msg}")
        # This could be a rate limit or a premium endpoint message. For this service's purpose,
        # it means no data is available. Return an empty DataFrame, let the caller handle it.
        return pd.DataFrame()

    ts_key = "Time Series (Daily)"
    if ts_key not in api_data:
        logger.error(f"No '{ts_key}' data found for {symbol}. API Response: {str(api_data)[:500]}")
        return pd.DataFrame()
        
    ts = api_data[ts_key]
    df = pd.DataFrame([
        {
            "date": pd.to_datetime(d_str).date(),
            "open": float(d_val["1. open"]),
            "high": float(d_val["2. high"]),
            "low": float(d_val["3. low"]),
            "close": float(d_val["4. close"]),
            "adjusted_close": float(d_val["5. adjusted close"]),
            "volume": int(d_val["6. volume"])
        }
        for d_str, d_val in ts.items()
    ])

    if df.empty:
        logger.warning(f"DataFrame became empty after parsing for {symbol}.")
        return pd.DataFrame()

    df = df.sort_values("date", ascending=True).reset_index(drop=True)
    
    if not date:
        df = df.tail(days).reset_index(drop=True)

    today = datetime.utcnow().date()
    df["date"] = pd.to_datetime(df["date"]).dt.date
    if today not in df["date"].values:
        latest_trading_day = df["date"].max()
        print(f"Today ({today}) is not a trading day. Using latest available trading day: {latest_trading_day}")
    else:
        latest_trading_day = today

    if not df.empty:
        logger.info(f"Successfully fetched {len(df)} days of data for {symbol}. Date range: {df['date'].min()} to {df['date'].max()}")
    else:
        logger.info(f"Fetched 0 days of data for {symbol} after all processing in fetch_price_data.")
        
    return df 

def calculate_price_volatility_features(df: pd.DataFrame) -> dict:
    """
    Calculates daily return, intraday volatility, and Bollinger Band %B from price data.
    """
    if df.empty or len(df) < 2:
        return {
            "daily_return": 0.0,
            "intraday_volatility": 0.0,
            "bollinger_percent_b": 0.0
        }

    latest = df.iloc[-1]
    previous = df.iloc[-2]

    # Daily Return
    daily_return = (latest['close'] - previous['close']) / previous['close']

    # Intraday Volatility
    intraday_volatility = (latest['high'] - latest['low']) / latest['close'] if latest['close'] > 0 else 0

    # Bollinger Band %B
    try:
        bbands = ta.bbands(df['close'], length=20, std=2)
        if bbands is not None and not bbands.empty:
            latest_bb = bbands.iloc[-1]
            upper_band = latest_bb['BBU_20_2.0']
            lower_band = latest_bb['BBL_20_2.0']
            
            if (upper_band - lower_band) > 0:
                bollinger_percent_b = (latest['close'] - lower_band) / (upper_band - lower_band)
            else:
                bollinger_percent_b = 0.0 # Avoid division by zero
        else:
            bollinger_percent_b = 0.0
    except Exception as e:
        print(f"Could not calculate Bollinger Bands: {e}")
        bollinger_percent_b = 0.0

    return {
        "daily_return": daily_return,
        "intraday_volatility": intraday_volatility,
        "bollinger_percent_b": bollinger_percent_b
    }

def fetch_rsi(symbol: str, api_key: str, interval: str = "daily", time_period: int = 14) -> float:
    """Fetch the latest RSI value for a symbol from Alpha Vantage."""
    url = f"https://www.alphavantage.co/query?function=RSI&symbol={symbol}&interval={interval}&time_period={time_period}&series_type=close&apikey={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if "Technical Analysis: RSI" in data:
            rsi_data = data["Technical Analysis: RSI"]
            if rsi_data:
                # Get the latest RSI value
                latest_date = sorted(rsi_data.keys())[-1]
                return float(rsi_data[latest_date]["RSI"])
        if "Error Message" in data:
            raise HTTPException(status_code=500, detail=f"Alpha Vantage RSI error: {data['Error Message']}")
        if "Information" in data:
            raise HTTPException(status_code=429, detail=f"Alpha Vantage RSI info: {data['Information']}")
        return 0.0
    except Exception as e:
        logger.error(f"Failed to fetch RSI for {symbol}: {e}")
        return 0.0 
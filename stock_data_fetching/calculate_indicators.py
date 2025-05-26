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
    return df 
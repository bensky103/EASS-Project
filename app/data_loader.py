     import yfinance as yf
     import pandas as pd

     def fetch_historical_data(symbol, period="60d", interval="1d"):
         ticker = yf.Ticker(symbol)
         hist = ticker.history(period=period, interval=interval)
         return hist['Close'].values  # or adjust as per your model's needs
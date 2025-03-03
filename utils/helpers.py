# helpers.py
import yfinance as yf

def fetch_historical_data(symbol, start="2023-01-01", end="2024-01-01"):
    """
    Fetch historical stock data from Yahoo Finance.
    """
    data = yf.download(symbol, start=start, end=end)
    return data

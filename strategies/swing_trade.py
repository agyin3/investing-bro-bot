import pandas as pd
from data.market_data import get_historical_data

def swing_trade_strategy(symbol):
    df = get_historical_data(symbol, "2024-01-01", "2024-03-01", timeframe="day")

    # Calculate Indicators
    df["SMA_50"] = df["close"].rolling(window=50).mean()
    df["SMA_200"] = df["close"].rolling(window=200).mean()
    df["MACD"] = df["close"].ewm(span=12).mean() - df["close"].ewm(span=26).mean()
    df["MACD_Signal"] = df["MACD"].ewm(span=9).mean()

    df["Signal"] = 0
    df.loc[(df["SMA_50"] > df["SMA_200"]) & (df["MACD"] > df["MACD_Signal"]), "Signal"] = 1  # Buy
    df.loc[(df["SMA_50"] < df["SMA_200"]) & (df["MACD"] < df["MACD_Signal"]), "Signal"] = -1  # Sell

    return df

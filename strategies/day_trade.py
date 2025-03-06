from data.market_data import get_historical_data

def day_trade_strategy(symbol):
    df = get_historical_data(symbol, "2024-03-01", "2024-03-04", timeframe="5Min")

    df["SMA_10"] = df["close"].rolling(window=10).mean()
    df["MACD"] = df["close"].ewm(span=12).mean() - df["close"].ewm(span=26).mean()
    df["MACD_Signal"] = df["MACD"].ewm(span=9).mean()

    df["Signal"] = 0
    df.loc[(df["close"] > df["SMA_10"]) & (df["MACD"] > df["MACD_Signal"]), "Signal"] = 1  # Buy
    df.loc[(df["close"] < df["SMA_10"]) & (df["MACD"] < df["MACD_Signal"]), "Signal"] = -1  # Sell

    return df

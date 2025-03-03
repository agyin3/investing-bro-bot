import os
from dotenv import load_dotenv
import backtrader as bt
import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from notifications.telegram_bot import send_telegram_alert
from strategies.vwap_strategy import VWAPStrategy

# Load environment variables
load_dotenv()
ALPACA_TEST_API_KEY = os.getenv("ALPACA_TEST_API_KEY")
ALPACA_TEST_SECRET_KEY = os.getenv("ALPACA_TEST_SECRET_KEY")

# Custom Pandas Data Feed
class CustomPandasData(bt.feeds.PandasData):
    params = (
        ("datetime", None),
        ("open", -1),
        ("high", -1),
        ("low", -1),
        ("close", -1),
        ("volume", -1),
    )
    datafields = ["datetime", "open", "high", "low", "close", "volume"]

# Backtesting Function
def backtest_strategy(symbol: str, strategy=VWAPStrategy):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy)

    # Initialize Alpaca Client
    client = StockHistoricalDataClient(ALPACA_TEST_API_KEY, ALPACA_TEST_SECRET_KEY)
    
    # Fetch Historical Data
    request_params = StockBarsRequest(symbol_or_symbols=symbol, timeframe=TimeFrame.Day, limit=1000)
    bars = client.get_stock_bars(request_params).df

    if bars.empty or len(bars) < 20:
        print(f"❌ Not enough data points for {symbol}. Backtest aborted.")
        send_telegram_alert(f"❌ Not enough data points for {symbol}.")
        return {"success": False, "final_value": None}

    # Convert to Backtrader format
    df = bars[["open", "high", "low", "close", "volume"]].copy()
    df.index = pd.to_datetime(df.index, format='%Y-%m-%d').tz_localize(None)
    df = df.sort_index()
    df = df.loc[~df.index.duplicated(keep="first")]

    # Debugging
    print(f"📊 Data Preview for {symbol}:")
    print(df.head())

    # Convert DataFrame to Backtrader Data Feed
    data = CustomPandasData(dataname=df)
    cerebro.adddata(data)
    cerebro.broker.set_cash(100)

    print(f"Starting Portfolio Value: {cerebro.broker.getvalue()}")
    cerebro.run()
    final_value = cerebro.broker.getvalue()
    print(f"Ending Portfolio Value: {final_value}")

    cerebro.plot()
    send_telegram_alert(f"📊 Backtest Completed for {symbol}")

    return {"success": final_value >= 120, "final_value": final_value}

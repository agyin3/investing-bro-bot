import backtrader as bt
import alpaca_trade_api as tradeapi
import pandas as pd
from config.config import ALPACA_TEST_API_KEY, ALPACA_TEST_SECRET_KEY, ALPACA_TEST_BASE_URL
from notifications.telegram_bot import send_telegram_alert
from datetime import datetime, timedelta

# Strategies 
from strategies.vwap_strategy import VWAPStrategy 
from strategies.sma_crossover import SMA_CrossStrategy

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

    # Initialize Alpaca API
    api = tradeapi.REST(ALPACA_TEST_API_KEY, ALPACA_TEST_SECRET_KEY, ALPACA_TEST_BASE_URL, api_version='v2')

    try:
        # Define date range
        end_date = datetime.today().strftime('%Y-%m-%d')
        start_date = (datetime.today() - timedelta(days=200)).strftime('%Y-%m-%d')  # 1000 days back


        # Fetch Historical Data
        bars = api.get_bars(symbol, timeframe='1Day', start=start_date, end=end_date, feed='iex').df

        print(f"✅ Retrieved {len(bars)} data points for {symbol} from {start_date} to {end_date}")

        # Ensure DataFrame contains expected columns
        required_columns = {"open", "high", "low", "close", "volume"}
        if not required_columns.issubset(bars.columns):
            print(f"❌ Invalid data format for {symbol}. Backtest aborted.")
            send_telegram_alert(f"❌ Invalid data format for {symbol}.")
            return

        # Format Data for Backtrader
        df = bars[["open", "high", "low", "close", "volume"]].copy()
        df.index = pd.to_datetime(df.index, format='%Y-%m-%d').tz_localize(None)
        df = df.sort_index()
        df = df.loc[~df.index.duplicated(keep="first")]

        if df.shape[0] < 20:
            print(f"❌ Not enough data points for {symbol}. Backtest aborted.")
            send_telegram_alert(f"❌ Not enough data points for {symbol}.")
            return

        # Debugging
        print(f"📊 Data Preview for {symbol}:")
        print(df.head())

        # Convert DataFrame to Backtrader Data Feed
        data = CustomPandasData(dataname=df)
        cerebro.adddata(data)

        cerebro.broker.set_cash(10000)

        print(f"Starting Portfolio Value: {cerebro.broker.getvalue()}")
        cerebro.run()
        print(f"Ending Portfolio Value: {cerebro.broker.getvalue()}")

        cerebro.plot()
        send_telegram_alert(f"📊 Backtest Completed for {symbol}")

    except Exception as e:
        error_message = f"⚠️ Backtest Error: {e}"
        print(error_message)
        send_telegram_alert(error_message)

# Run Backtest for AAPL
if __name__ == "__main__":
    backtest_strategy("AAPL", VWAPStrategy)

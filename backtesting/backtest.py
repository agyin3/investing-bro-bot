import backtrader as bt
import pandas as pd
from datetime import datetime, timedelta
from data.market_data import get_historical_data

class DayTradeStrategy(bt.Strategy):
    params = (("sma_period", 10),)

    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.sma_period)
        self.macd = bt.indicators.MACD(self.data.close)
        self.trades = 0
        self.wins = 0

    def next(self):
        if not self.position:
            if self.data.close[0] > self.sma[0] and self.macd.macd[0] > self.macd.signal[0]:
                self.buy()
                self.trades += 1
        else:
            if self.data.close[0] < self.sma[0] and self.macd.macd[0] < self.macd.signal[0]:
                if self.data.close[0] > self.position.price:
                    self.wins += 1
                self.sell()

class BacktestStrategy(bt.Strategy):
    params = (
        ("short_window", 10),
        ("long_window", 50),
    )

    def __init__(self):
        self.sma_short = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.short_window)
        self.sma_long = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.long_window)
        self.macd = bt.indicators.MACD(self.data.close)
        self.trades = 0
        self.wins = 0

    def next(self):
        if not self.position:
            if self.sma_short[0] > self.sma_long[0] and self.macd.macd[0] > self.macd.signal[0]:
                self.buy()
                self.trades += 1
        else:
            if self.sma_short[0] < self.sma_long[0] and self.macd.macd[0] < self.macd.signal[0]:
                if self.data.close[0] > self.position.price:
                    self.wins += 1
                self.sell()

def get_dynamic_dates():
    """Returns the start and end dates for backtesting (last 1 year, ending yesterday)."""
    end_date = datetime.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=365)
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

def run_swing_trade_backtest(symbol, timeframe="day"):
    """Runs a swing trade backtest and returns performance metrics."""
    
    start_date, end_date = get_dynamic_dates()
    df = get_historical_data(symbol, start_date, end_date, timeframe)
    
    if df.empty:
        print(f"⚠️ No historical data available for {symbol}. Skipping swing trade backtest.")
        return None
    
    data = bt.feeds.PandasData(dataname=df)

    cerebro = bt.Cerebro()
    cerebro.addstrategy(BacktestStrategy)
    cerebro.adddata(data)
    cerebro.broker.set_cash(10000)
    cerebro.broker.setcommission(commission=0.001)

    starting_value = cerebro.broker.getvalue()
    
    try:
        results = cerebro.run()
    except Exception as e:
        print(f"❌ Swing trade backtest failed for {symbol}: {e}")
        return None

    final_value = cerebro.broker.getvalue()

    strategy = results[0]
    total_trades = strategy.trades
    win_rate = (strategy.wins / total_trades) * 100 if total_trades > 0 else 0
    profit_loss_pct = ((final_value - starting_value) / starting_value) * 100

    print(f"Swing Trade Backtest for {symbol}:")
    print(f" - Final Portfolio Value: ${final_value:.2f}")
    print(f" - Profit/Loss: {profit_loss_pct:.2f}%")
    print(f" - Win Rate: {win_rate:.2f}%")

    return {
        "symbol": symbol,
        "final_value": final_value,
        "profit_loss_pct": profit_loss_pct,
        "win_rate": win_rate
    }

def run_day_trade_backtest(symbol):
    """Runs a day trade backtest using 5-minute candles."""
    
    start_date, end_date = get_dynamic_dates()
    df = get_historical_data(symbol, start_date, end_date, timeframe="5Min")

    if df.empty:
        print(f"⚠️ No historical data available for {symbol}. Skipping day trade backtest.")
        return None
    
    data = bt.feeds.PandasData(dataname=df)
    cerebro = bt.Cerebro()
    cerebro.addstrategy(DayTradeStrategy)
    cerebro.adddata(data)
    cerebro.broker.set_cash(5000)
    cerebro.broker.setcommission(commission=0.002)

    starting_value = cerebro.broker.getvalue()

    try:
        results = cerebro.run()
    except Exception as e:
        print(f"❌ Day trade backtest failed for {symbol}: {e}")
        return None

    final_value = cerebro.broker.getvalue()

    strategy = results[0]
    total_trades = strategy.trades
    win_rate = (strategy.wins / total_trades) * 100 if total_trades > 0 else 0
    profit_loss_pct = ((final_value - starting_value) / starting_value) * 100

    print(f"Day Trade Backtest for {symbol}:")
    print(f" - Final Portfolio Value: ${final_value:.2f}")
    print(f" - Profit/Loss: {profit_loss_pct:.2f}%")
    print(f" - Win Rate: {win_rate:.2f}%")

    return {
        "symbol": symbol,
        "final_value": final_value,
        "profit_loss_pct": profit_loss_pct,
        "win_rate": win_rate
    }

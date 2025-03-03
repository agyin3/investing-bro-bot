import backtrader as bt
import numpy as np

class VWAPStrategy(bt.Strategy):
    params = dict(period=14)  # Lookback period for VWAP

    def __init__(self):
        self.vwap = bt.indicators.WeightedMovingAverage(self.data.close * self.data.volume, period=self.params.period) / \
                    bt.indicators.WeightedMovingAverage(self.data.volume, period=self.params.period)

    def next(self):
        price = self.data.close[0]

        # Buy Signal: When price crosses above VWAP
        if price > self.vwap[0] and not self.position:
            self.buy()
            print(f"📈 BUY: {self.data.datetime.date(0)}, Price: {price}, VWAP: {self.vwap[0]}")

        # Sell Signal: When price crosses below VWAP
        elif price < self.vwap[0] and self.position:
            self.sell()
            print(f"📉 SELL: {self.data.datetime.date(0)}, Price: {price}, VWAP: {self.vwap[0]}")

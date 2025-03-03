import backtrader as bt

class SMA_CrossStrategy(bt.Strategy):
    params = ("short_period", 50), ("long_period", 200)

    def __init__(self):
        self.sma_short = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.short_period)
        self.sma_long = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.long_period)

    def next(self):
        if self.sma_short[0] > self.sma_long[0]:  # Buy Signal
            if not self.position:
                self.buy()
        elif self.sma_short[0] < self.sma_long[0]:  # Sell Signal
            if self.position:
                self.sell()

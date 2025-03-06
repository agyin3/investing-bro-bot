import backtrader as bt

class EMACrossoverStrategy(bt.Strategy):
    params = dict(short_period=9, long_period=21)

    def __init__(self):
        self.ema_short = bt.indicators.EMA(period=self.params.short_period)
        self.ema_long = bt.indicators.EMA(period=self.params.long_period)

    def next(self):
        if not self.position:
            if self.ema_short[0] > self.ema_long[0] and self.ema_short[-1] <= self.ema_long[-1]:
                self.buy()
        else:
            if self.ema_short[0] < self.ema_long[0] and self.ema_short[-1] >= self.ema_long[-1]:
                self.sell()

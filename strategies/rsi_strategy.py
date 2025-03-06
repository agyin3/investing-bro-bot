import backtrader as bt

class RSIStrategy(bt.Strategy):
    params = dict(rsi_period=14, rsi_oversold=30, rsi_overbought=70)

    def __init__(self):
        self.rsi = bt.indicators.RSI(period=self.params.rsi_period)

    def next(self):
        if not self.position:
            if self.rsi < self.params.rsi_oversold:
                self.buy()
        else:
            if self.rsi > self.params.rsi_overbought:
                self.sell()

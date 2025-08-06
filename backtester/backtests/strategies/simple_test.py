"""
Simple test strategy to verify backtrader is working properly
"""

import backtrader as bt

class SimpleTestStrategy(bt.Strategy):
    def __init__(self):
        self.sma20 = bt.indicators.SMA(self.data.close, period=20)
        self.sma50 = bt.indicators.SMA(self.data.close, period=50)
        
    def next(self):
        if not self.position:
            if self.sma20[0] > self.sma50[0]:
                self.buy(size=1)
        else:
            if self.sma20[0] < self.sma50[0]:
                self.sell(size=1)

if __name__ == '__main__':
    # This is a test file, not a standalone runner
    pass
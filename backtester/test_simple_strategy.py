#!/usr/bin/env python3
"""
Simple test strategy to debug the backtrader setup
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import backtrader as bt
import pandas as pd
import datetime


class FourSwordsCSVData(bt.feeds.GenericCSVData):
    """
    Custom CSV data feed for Four Swords strategy
    """
    params = (
        ('datetime', 0),  
        ('open', 1),      
        ('high', 2),      
        ('low', 3),       
        ('close', 4),     
        ('volume', 5),    
        ('openinterest', -1),  
        ('dtformat', '%Y-%m-%d %H:%M:%S'),    
        ('tmformat', '%H:%M:%S'),
    )

    def _loadline(self, linetokens):
        try:
            # Handle timestamp (milliseconds)
            dt_str = linetokens[self.p.datetime]
            timestamp = float(dt_str)
            if timestamp > 1e10:  # milliseconds
                timestamp = timestamp / 1000
            dt = datetime.datetime.fromtimestamp(timestamp)
            linetokens[self.p.datetime] = dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            print(f"Error processing line: {e}")
            return False
        
        return super()._loadline(linetokens)


class SimpleTestStrategy(bt.Strategy):
    """
    Simple Buy and Hold strategy for testing
    """
    
    params = (
        ('position_pct', 0.05),
    )
    
    def __init__(self):
        # Simple moving average
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=20)
        
    def next(self):
        if not self.position:
            if self.data.close[0] > self.sma[0]:
                size = self.broker.getvalue() * self.params.position_pct / self.data.close[0]
                self.buy(size=size)
        elif self.data.close[0] < self.sma[0]:
            self.close()
    
    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                print(f'BUY EXECUTED - Price: {order.executed.price:.2f}')
            elif order.issell():
                print(f'SELL EXECUTED - Price: {order.executed.price:.2f}')


def main():
    # Initialize Cerebro
    cerebro = bt.Cerebro()
    
    # Set broker parameters
    cerebro.broker.setcash(500.0)
    cerebro.broker.setcommission(commission=0.0002)
    
    # Load data
    data_path = "backtester/data/BTCUSDT/4h/BTCUSDT-4h-merged.csv"
    
    if not os.path.exists(data_path):
        print(f"Data file not found: {data_path}")
        return
    
    print(f"Loading data from: {data_path}")
    
    # Create data feed
    data_feed = FourSwordsCSVData(
        dataname=data_path,
        timeframe=bt.TimeFrame.Minutes,
        compression=1,
    )
    cerebro.adddata(data_feed)
    
    # Add strategy
    cerebro.addstrategy(SimpleTestStrategy, position_pct=0.05)
    
    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    
    print(f"Starting Portfolio Value: ${cerebro.broker.getvalue():.2f}")
    
    # Run backtest
    try:
        results = cerebro.run()
        strategy = results[0]
        
        print(f"Final Portfolio Value: ${cerebro.broker.getvalue():.2f}")
        
        # Print basic results
        trade_analyzer = strategy.analyzers.trades.get_analysis()
        returns_analyzer = strategy.analyzers.returns.get_analysis()
        
        total_trades = trade_analyzer.total.closed if hasattr(trade_analyzer, 'total') else 0
        print(f"Total Trades: {total_trades}")
        
        if hasattr(returns_analyzer, 'rtot'):
            total_return = returns_analyzer.rtot * 100
            print(f"Total Return: {total_return:.2f}%")
        
    except Exception as e:
        print(f"Backtest failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
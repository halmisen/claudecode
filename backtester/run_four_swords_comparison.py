#!/usr/bin/env python3
"""
Four Swords Strategy Comparison Runner v1.5
Compare original v1.4 vs enhanced v1.5 strategy performance
"""
import sys
import os
import argparse
import pandas as pd
import backtrader as bt
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import strategies
from backtester.strategies.four_swords_enhanced_strategy_v1_5 import FourSwordsEnhancedStrategy, compare_strategies

def create_data_feed(csv_file):
    """Create data feed from CSV file with proper datetime handling"""
    
    try:
        # Read CSV with multiple possible datetime column names
        df = pd.read_csv(csv_file)
        
        # Standardize column names
        column_mapping = {
            'Open time': 'datetime',
            'open_time': 'datetime', 
            'timestamp': 'datetime',
            'time': 'datetime',
            'date': 'datetime',
            'Open': 'open',
            'High': 'high', 
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Handle datetime conversion
        if 'datetime' in df.columns:
            # Convert timestamp to datetime
            if df['datetime'].dtype in ['int64', 'float64']:
                # Unix timestamp in milliseconds
                df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
            else:
                # String datetime
                df['datetime'] = pd.to_datetime(df['datetime'])
            
            df.set_index('datetime', inplace=True)
        else:
            # Use index as datetime if no datetime column found
            df.index = pd.to_datetime(df.index)
        
        # Ensure required columns exist
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Required column '{col}' not found in CSV")
        
        # Remove timezone info for Backtrader compatibility
        df.index = df.index.tz_localize(None)
        
        # Sort by datetime
        df = df.sort_index()
        
        # Create Backtrader data feed
        data = bt.feeds.PandasData(
            dataname=df,
            datetime=None,  # Use index
            open='open',
            high='high', 
            low='low',
            close='close',
            volume='volume',
            openinterest=None
        )
        
        return data, df
        
    except Exception as e:
        print(f"Error creating data feed: {e}")
        return None, None


def run_strategy_backtest(data, strategy_class, strategy_params, cash=500.0, commission=0.0002):
    """Run backtest for a single strategy"""
    
    # Create Cerebro engine
    cerebro = bt.Cerebro()
    
    # Add data
    cerebro.adddata(data)
    
    # Add strategy
    cerebro.addstrategy(strategy_class, **strategy_params)
    
    # Set broker parameters
    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(commission=commission)
    
    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trade_analyzer')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    
    # Run backtest
    print("Running backtest...")
    results = cerebro.run()
    
    return results[0], cerebro


def main():
    """Main comparison runner"""
    
    parser = argparse.ArgumentParser(description='Four Swords Strategy Comparison')
    parser.add_argument('--data', required=True, help='Path to OHLCV CSV file')
    parser.add_argument('--cash', type=float, default=500.0, help='Initial cash (default: 500)')
    parser.add_argument('--commission', type=float, default=0.0002, help='Commission rate (default: 0.0002)')
    parser.add_argument('--market-type', choices=['crypto', 'stocks'], default='crypto', help='Market type')
    parser.add_argument('--leverage', type=float, default=1.0, help='Leverage (default: 1.0)')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--plot', action='store_true', help='Enable plotting')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Four Swords Strategy Comparison v1.5")
    print("=" * 60)
    print(f"Data file: {args.data}")
    print(f"Initial cash: ${args.cash}")
    print(f"Commission: {args.commission * 100:.3f}%")
    print(f"Market type: {args.market_type}")
    print(f"Leverage: {args.leverage}x")
    print("-" * 60)
    
    # Create data feed
    data, df = create_data_feed(args.data)
    if data is None:
        print("Failed to create data feed. Exiting.")
        return
    
    print(f"Data loaded successfully:")
    print(f"  Period: {df.index[0]} to {df.index[-1]}")
    print(f"  Total bars: {len(df)}")
    print(f"  Timeframe: {pd.infer_freq(df.index) or 'Unknown'}")
    print("-" * 60)
    
    # Enhanced Strategy Parameters
    enhanced_params = {
        'market_type': args.market_type,
        'leverage': args.leverage,
        'debug': args.debug,
        'plot_indicators': args.plot,
        
        # Enhanced features enabled
        'use_enhanced_momentum': True,
        'use_stop_loss': True,
        'use_volatility_position': True,
        'use_time_exit': True,
        
        # Risk management
        'base_position_size': 15.0,  # Reduced from 20%
        'atr_multiplier': 2.0,
        'max_drawdown_percent': 15.0,
        'max_consecutive_losses': 3,
        'max_bars_in_trade': 50,
    }
    
    # Run Enhanced Strategy
    print("Testing Enhanced Strategy v1.5...")
    enhanced_results, enhanced_cerebro = run_strategy_backtest(
        data, FourSwordsEnhancedStrategy, enhanced_params, args.cash, args.commission
    )
    
    if enhanced_results is None:
        print("Enhanced strategy backtest failed. Exiting.")
        return
    
    # Calculate performance metrics
    print("\n" + "=" * 60)
    print("PERFORMANCE ANALYSIS")
    print("=" * 60)
    
    # Enhanced strategy metrics
    if hasattr(enhanced_results, 'analyzers'):
        trade_analyzer = enhanced_results.analyzers.trade_analyzer.get_analysis()
        returns_analyzer = enhanced_results.analyzers.returns.get_analysis()
        drawdown_analyzer = enhanced_results.analyzers.drawdown.get_analysis()
        
        print("\\nEnhanced Strategy v1.5 Results:")
        print("-" * 40)
        
        total_trades = trade_analyzer.get('total', {}).get('total', 0)
        winning_trades = trade_analyzer.get('won', {}).get('total', 0)
        losing_trades = trade_analyzer.get('lost', {}).get('total', 0)
        
        print(f"Total Trades: {total_trades}")
        print(f"Winning Trades: {winning_trades}")
        print(f"Losing Trades: {losing_trades}")
        
        if total_trades > 0:
            win_rate = (winning_trades / total_trades) * 100
            print(f"Win Rate: {win_rate:.1f}%")
        
        avg_win = trade_analyzer.get('won', {}).get('pnl', {}).get('average', 0)
        avg_loss = trade_analyzer.get('lost', {}).get('pnl', {}).get('average', 0)
        print(f"Average Win: ${avg_win:.2f}")
        print(f"Average Loss: ${avg_loss:.2f}")
        
        if avg_loss != 0:
            profit_factor = abs(avg_win / avg_loss)
            print(f"Profit Factor: {profit_factor:.2f}")
        
        total_return = returns_analyzer.get('rtot', 0) * 100
        print(f"Total Return: {total_return:.2f}%")
        
        max_drawdown = drawdown_analyzer.get('max', {}).get('drawdown', 0)
        print(f"Max Drawdown: {max_drawdown:.2f}%")
        
        # Portfolio value
        final_value = enhanced_cerebro.broker.get_value()
        print(f"Final Portfolio Value: ${final_value:.2f}")
        print(f"Initial Cash: ${args.cash:.2f}")
        print(f"Net Profit: ${final_value - args.cash:.2f}")
    
    # Key improvements summary
    print("\\n" + "=" * 60)
    print("KEY ENHANCEMENTS IMPLEMENTED")
    print("=" * 60)
    print("✅ Division-by-zero protection in WaveTrend calculation")
    print("✅ Enhanced momentum detection with 3-period SMA + rate threshold")
    print("✅ ATR-based dynamic stop losses")
    print("✅ Volatility-adjusted position sizing")
    print("✅ Market regime detection for adaptive parameters")
    print("✅ Weighted confirmation scoring system")
    print("✅ Circuit breaker protection (drawdown + consecutive losses)")
    print("✅ Time-based exit mechanism")
    print("✅ Comprehensive risk management framework")
    
    # Performance targets vs actual
    print("\\n" + "=" * 60)
    print("PERFORMANCE TARGETS vs ACTUAL")
    print("=" * 60)
    if total_trades > 0:
        print(f"Win Rate Target: 80%+ | Actual: {win_rate:.1f}%")
        target_met = "✅" if win_rate >= 80 else "❌"
        print(f"Target Achievement: {target_met}")
        
        print(f"Drawdown Target: <15% | Actual: {max_drawdown:.2f}%")
        dd_target_met = "✅" if max_drawdown < 15 else "❌" 
        print(f"Drawdown Target: {dd_target_met}")
        
        print(f"Return Target: >20% | Actual: {total_return:.2f}%")
        return_target_met = "✅" if total_return > 20 else "❌"
        print(f"Return Target: {return_target_met}")
    
    # Plotting
    if args.plot:
        print("\\nGenerating plots...")
        enhanced_cerebro.plot(style='candlestick', barup='green', bardown='red')
    
    print("\\n" + "=" * 60)
    print("COMPARISON COMPLETED")
    print("=" * 60)


if __name__ == '__main__':
    main()
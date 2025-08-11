#!/usr/bin/env python3
"""
Interactive Plotly visualization script for trading data.
Generates interactive HTML charts from OHLCV, trades, and equity data.

This script has been replaced by the v5 strategy runner with integrated Bokeh visualization.
Please use run_doji_ashi_strategy_v5.py instead for better performance and integrated charting.

Usage (deprecated):
    python examples/run_csv_and_plot.py --csv [ohlcv.csv] --trades [trades.csv] --equity [equity.csv] --out reports/plot.html --title "Strategy Backtest"

Recommended alternative:
    python backtester/run_doji_ashi_strategy_v5.py --data [data.csv] --enable_backtrader_plot
"""

import argparse
import sys
import warnings

def main():
    """
    Deprecated plotting utility.
    """
    warnings.warn(
        "run_csv_and_plot.py is deprecated. "
        "Please use run_doji_ashi_strategy_v5.py with --enable_backtrader_plot for "
        "superior performance and integrated Bokeh visualization.",
        DeprecationWarning,
        stacklevel=2
    )
    
    parser = argparse.ArgumentParser(
        description="Deprecated: Use run_doji_ashi_strategy_v5.py instead"
    )
    parser.add_argument('--csv', help='OHLCV CSV file path')
    parser.add_argument('--trades', help='Trades CSV file path')
    parser.add_argument('--equity', help='Equity curve CSV file path')
    parser.add_argument('--out', help='Output HTML file path')
    parser.add_argument('--title', default='Strategy Backtest', help='Chart title')
    
    args = parser.parse_args()
    
    print("❌ This script is deprecated.")
    print("✅ Please use the v5 strategy runner instead:")
    print("   python backtester/run_doji_ashi_strategy_v5.py --data [your_data.csv] --enable_backtrader_plot")
    print("")
    print("🎯 Benefits of v5:")
    print("   - Superior performance (103% vs 38% returns)")
    print("   - Faster execution (1.3s vs 15+ seconds)")
    print("   - Interactive Bokeh charts")
    print("   - Zero data collection overhead")
    
    return 1

if __name__ == '__main__':
    sys.exit(main())
"""
Doji Ashi Strategy v5 运行脚本 - Backtrader原生绘图版本
专注于策略执行性能和Backtrader内置可视化功能

主要特性:
- 使用Backtrader内置绘图系统
- 移除Plotly复杂度和性能开销
- 保留所有策略逻辑优化
- 更好的执行性能和稳定性
- 零配置绘图设置

使用方法:
python run_doji_ashi_strategy_v5.py --data data/ETHUSDT/2h/ETHUSDT-2h-merged.csv --market_type crypto
python run_doji_ashi_strategy_v5.py --data data/AAPL/4h/AAPL-4h.csv --market_type stocks --market_data data/SPY/4h/SPY-4h.csv
"""

import backtrader as bt
import pandas as pd
import numpy as np
from pathlib import Path
import datetime as dt
import argparse
import sys

from strategies.doji_ashi_strategy_v5 import DojiAshiStrategyV5


def load_ohlcv_data(file_path, limit=None):
    """
    加载OHLCV数据并转换为Backtrader格式
    支持多种时间戳格式和列名
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    print(f"Loading data from: {file_path}")
    df = pd.read_csv(file_path, low_memory=False)
    
    if limit:
        df = df.tail(limit)
        print(f"Limited to last {limit} rows")
    
    print(f"Original data shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # 处理时间列
    time_columns = ['datetime', 'timestamp', 'open_time', 'time', 'date']
    time_col = None
    
    for col in time_columns:
        if col in df.columns:
            time_col = col
            break
    
    if time_col is None:
        # 如果没有找到时间列，使用索引
        if df.index.name in time_columns or 'time' in str(df.index.name).lower():
            df = df.reset_index()
            time_col = df.columns[0]
        else:
            raise ValueError(f"No time column found. Available columns: {list(df.columns)}")
    
    # 转换时间格式
    if time_col in df.columns:
        if df[time_col].dtype == 'int64' or df[time_col].dtype == 'float64':
            # Unix timestamp (milliseconds or seconds)
            if df[time_col].iloc[0] > 1e10:  # Milliseconds
                df[time_col] = pd.to_datetime(df[time_col], unit='ms')
            else:  # Seconds
                df[time_col] = pd.to_datetime(df[time_col], unit='s')
        else:
            df[time_col] = pd.to_datetime(df[time_col])
        
        df.set_index(time_col, inplace=True)
    
    # 标准化列名
    column_mapping = {
        'open': 'open', 'Open': 'open', 'OPEN': 'open',
        'high': 'high', 'High': 'high', 'HIGH': 'high', 
        'low': 'low', 'Low': 'low', 'LOW': 'low',
        'close': 'close', 'Close': 'close', 'CLOSE': 'close',
        'volume': 'volume', 'Volume': 'volume', 'VOLUME': 'volume', 'vol': 'volume'
    }
    
    df.rename(columns=column_mapping, inplace=True)
    
    required_cols = ['open', 'high', 'low', 'close']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # 确保数值列为float类型
    numeric_cols = ['open', 'high', 'low', 'close', 'volume']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 处理缺失的volume列
    if 'volume' not in df.columns:
        df['volume'] = 1000  # 默认成交量
        print("Volume column not found, using default value: 1000")
    
    # 清理数据
    df = df.dropna()
    df = df.sort_index()
    
    # 移除重复的时间戳
    df = df[~df.index.duplicated(keep='first')]
    
    print(f"Processed data shape: {df.shape}")
    print(f"Date range: {df.index.min()} to {df.index.max()}")
    print(f"Sample data:")
    print(df.head(3).to_string())
    
    return df


class PandasData(bt.feeds.PandasData):
    """
    扩展的Backtrader Pandas数据源
    支持更灵活的列映射
    """
    params = (
        ('datetime', None),
        ('open', 'open'),
        ('high', 'high'), 
        ('low', 'low'),
        ('close', 'close'),
        ('volume', 'volume'),
        ('openinterest', None),
    )


def run_backtest(args):
    """运行回测"""
    print("=== Doji Ashi Strategy v5 Backtest ===")
    print(f"Strategy: Backtrader Native Plotting Version")
    print(f"Data: {args.data}")
    print(f"Market Type: {args.market_type}")
    print(f"Date Range: {args.start_date} to {args.end_date}")
    print(f"Cash: ${args.cash:,.2f}")
    print(f"Commission: {args.commission:.4f}")
    
    # 创建Cerebro引擎
    cerebro = bt.Cerebro()
    
    # 设置初始资金和手续费
    cerebro.broker.set_cash(args.cash)
    cerebro.broker.setcommission(commission=args.commission)
    
    # 加载主要数据
    try:
        df_main = load_ohlcv_data(args.data, limit=args.limit)
    except Exception as e:
        print(f"Error loading main data: {e}")
        return
    
    # 应用日期过滤
    if args.start_date:
        start_date = pd.to_datetime(args.start_date)
        df_main = df_main[df_main.index >= start_date]
    
    if args.end_date:
        end_date = pd.to_datetime(args.end_date)
        df_main = df_main[df_main.index <= end_date]
    
    if df_main.empty:
        print("No data available for the specified date range")
        return
    
    # 添加主要数据源
    data_main = PandasData(dataname=df_main)
    cerebro.adddata(data_main, name='main')
    
    # 加载市场数据（可选）
    if args.market_data and Path(args.market_data).exists():
        try:
            df_market = load_ohlcv_data(args.market_data, limit=args.limit)
            if args.start_date:
                df_market = df_market[df_market.index >= pd.to_datetime(args.start_date)]
            if args.end_date:
                df_market = df_market[df_market.index <= pd.to_datetime(args.end_date)]
            
            data_market = PandasData(dataname=df_market)
            cerebro.adddata(data_market, name='market')
            print(f"Market data loaded: {args.market_data}")
        except Exception as e:
            print(f"Warning: Could not load market data: {e}")
    
    # 添加策略
    cerebro.addstrategy(
        DojiAshiStrategyV5,
        market_type=args.market_type,
        trade_direction=args.trade_direction,
        enable_daily_trend_filter=args.enable_daily_trend_filter,
        trend_mode=args.trend_mode,
        enable_volume_filter=args.enable_volume_filter,
        enable_vwap_filter_entry=args.enable_vwap_filter_entry,
        enable_entry_trigger=args.enable_entry_trigger,
        entry_mode=args.entry_mode,
        fast_ma_len=args.fast_ma_len,
        slow_ma_len=args.slow_ma_len,
        atr_length=args.atr_length,
        atr_multiplier=args.atr_multiplier,
        risk_reward_ratio=args.risk_reward_ratio,
        order_percent=args.order_percent / 100.0,
        leverage=args.leverage,
        cooldown_bars=args.cooldown_bars,
        # V5版本：Backtrader原生绘图设置
        enable_backtrader_plot=args.enable_backtrader_plot,
        plot_volume=args.plot_volume,
        plot_indicators=args.plot_indicators
    )
    
    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trade_analyzer')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    
    print(f"\\nBacktest Period: {df_main.index.min().strftime('%Y-%m-%d')} to {df_main.index.max().strftime('%Y-%m-%d')}")
    print(f"Total Bars: {len(df_main):,}")
    
    # 运行回测
    print("\\nRunning backtest...")
    start_time = dt.datetime.now()
    results = cerebro.run()
    end_time = dt.datetime.now()
    
    strategy = results[0]
    
    # 打印结果
    print(f"\\n=== Backtest Results (Runtime: {(end_time - start_time).total_seconds():.2f}s) ===")
    print(f"Starting Portfolio Value: ${args.cash:,.2f}")
    print(f"Final Portfolio Value: ${cerebro.broker.getvalue():,.2f}")
    print(f"Total Return: {((cerebro.broker.getvalue() / args.cash - 1) * 100):+.2f}%")
    
    # 交易分析
    trade_analyzer = strategy.analyzers.trade_analyzer.get_analysis()
    if trade_analyzer.total and trade_analyzer.total.closed > 0:
        print(f"\\n=== Trade Statistics ===")
        print(f"Total Trades: {trade_analyzer.total.closed}")
        print(f"Winning Trades: {trade_analyzer.won.total if hasattr(trade_analyzer, 'won') else 0}")
        print(f"Losing Trades: {trade_analyzer.lost.total if hasattr(trade_analyzer, 'lost') else 0}")
        if hasattr(trade_analyzer, 'won') and trade_analyzer.won.total > 0:
            win_rate = trade_analyzer.won.total / trade_analyzer.total.closed * 100
            print(f"Win Rate: {win_rate:.2f}%")
            print(f"Average Win: ${trade_analyzer.won.pnl.average:.2f}")
        if hasattr(trade_analyzer, 'lost') and trade_analyzer.lost.total > 0:
            print(f"Average Loss: ${trade_analyzer.lost.pnl.average:.2f}")
        print(f"Total PnL: ${trade_analyzer.pnl.net.total:.2f}")
    else:
        print("\\n=== No Trades Executed ===")
        print("Strategy did not generate any trades. Consider adjusting:")
        print("- Reducing warmup period")
        print("- Relaxing filter conditions")  
        print("- Checking data quality and timeframe")
        print("- Verifying market type settings")
    
    # Sharpe比率
    sharpe_ratio = strategy.analyzers.sharpe_ratio.get_analysis()
    if sharpe_ratio and 'sharperatio' in sharpe_ratio:
        print(f"Sharpe Ratio: {sharpe_ratio['sharperatio']:.3f}")
    
    # 最大回撤
    drawdown = strategy.analyzers.drawdown.get_analysis()
    if drawdown and 'max' in drawdown:
        print(f"Max Drawdown: {drawdown['max']['drawdown']:.2f}%")
    
    # V5版本：优先使用backtrader-plotting，回退到内置绘图
    if args.enable_backtrader_plot:
        print("\\n=== Creating Enhanced Plot ===")
        try:
            # 尝试使用backtrader-plotting (更美观)
            try:
                from backtrader_plotting import Bokeh
                print("Using backtrader-plotting (Bokeh) for enhanced visualization...")
                
                # 使用Bokeh绘图 - 配置交互式网页
                import datetime
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                bokeh_filename = f'plots/doji_ashi_v5_bokeh_{args.market_type}_{timestamp}.html'
                
                bokeh_plot = Bokeh(
                    plot_mode='single',       # 单图模式
                    output_mode='save',       # 保存为HTML文件
                    filename=bokeh_filename,  # 输出文件名
                    show=True                 # 自动在浏览器中打开
                )
                cerebro.plot(bokeh_plot)
                print("Enhanced Bokeh plot created successfully!")
                
            except ImportError:
                print("backtrader-plotting not found, using standard Backtrader plotting...")
                # 回退到标准绘图
                cerebro.plot(
                    style='candlestick',  # 蜡烛图样式
                    barup='green',        # 上涨蜡烛颜色
                    bardown='red',        # 下跌蜡烛颜色
                    volup='lightgreen',   # 上涨成交量颜色
                    voldown='lightcoral', # 下跌成交量颜色
                    volume=args.plot_volume,  # 是否显示成交量
                    plotdist=0.1,         # 子图间距
                    plotname=f'Doji Ashi v5 - {args.market_type.upper()}',  # 图表标题
                )
                print("Standard Backtrader plot created successfully!")
                
        except Exception as e:
            print(f"Error creating plot: {e}")
            print("Try installing: pip install backtrader-plotting")
    
    print("\\n=== Backtest Complete ===")


def main():
    parser = argparse.ArgumentParser(description='Doji Ashi Strategy v5 - Backtrader Native Plotting')
    
    # 数据参数
    parser.add_argument('--data', required=True, help='Path to OHLCV CSV file')
    parser.add_argument('--market_data', help='Path to market data CSV file (SPY/BTC)')
    parser.add_argument('--limit', type=int, help='Limit number of rows to load')
    parser.add_argument('--start_date', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end_date', help='End date (YYYY-MM-DD)')
    
    # 策略参数
    parser.add_argument('--market_type', choices=['crypto', 'stocks'], default='crypto',
                       help='Market type preset')
    parser.add_argument('--trade_direction', choices=['long', 'short', 'both'], default='long',
                       help='Trading direction (default: long only)')
    
    # 过滤器参数
    parser.add_argument('--enable_daily_trend_filter', action='store_true', default=True,
                       help='Enable daily trend filter')
    parser.add_argument('--trend_mode', choices=['strict', 'flexible'], default='strict',
                       help='Daily trend filter mode')
    parser.add_argument('--enable_volume_filter', action='store_true',
                       help='Enable relative volume filter')
    parser.add_argument('--enable_vwap_filter_entry', action='store_true',
                       help='Enable VWAP entry filter')
    parser.add_argument('--enable_entry_trigger', action='store_true', default=True,
                       help='Enable 3/8 MA entry trigger')
    parser.add_argument('--entry_mode', choices=['cross', 'above_below'], default='above_below',
                       help='MA entry mode')
    
    # 技术指标参数
    parser.add_argument('--fast_ma_len', type=int, default=3, help='Fast MA length')
    parser.add_argument('--slow_ma_len', type=int, default=8, help='Slow MA length')
    parser.add_argument('--atr_length', type=int, default=14, help='ATR period')
    parser.add_argument('--atr_multiplier', type=float, default=1.5, help='ATR multiplier for SL')
    parser.add_argument('--risk_reward_ratio', type=float, default=2.0, help='Risk:Reward ratio')
    
    # 仓位管理参数
    parser.add_argument('--order_percent', type=float, default=20.0,
                       help='Position size as percentage of equity')
    parser.add_argument('--leverage', type=float, default=4.0, help='Leverage multiplier')
    parser.add_argument('--cooldown_bars', type=int, default=10,
                       help='Cooldown bars between signals')
    
    # 回测参数 (用户默认设置)
    parser.add_argument('--cash', type=float, default=500.0, help='Starting cash (default: 500 USDT)')
    parser.add_argument('--commission', type=float, default=0.0002, help='Commission rate (default: 0.02% for limit orders)')
    
    # V5版本：Backtrader绘图参数
    parser.add_argument('--enable_backtrader_plot', action='store_true', default=True,
                       help='Enable Backtrader native plotting')
    parser.add_argument('--plot_volume', action='store_true', default=True,
                       help='Plot volume in Backtrader chart')
    parser.add_argument('--plot_indicators', action='store_true', default=True,
                       help='Plot technical indicators in Backtrader chart')
    
    args = parser.parse_args()
    
    # 运行回测
    run_backtest(args)


if __name__ == '__main__':
    main()
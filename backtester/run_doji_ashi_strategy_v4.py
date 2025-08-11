"""
Doji Ashi Strategy v4 运行脚本 - 集成 Plotly + plotly-resampler
支持高级交互式可视化、大数据集性能优化和详细的技术指标展示

主要特性:
- 高质量 Plotly 交互式图表
- plotly-resampler 大数据集优化
- 详细的技术指标和交易信号可视化
- 自定义图表样式和主题
- 多时间框架数据展示

使用方法:
python run_doji_ashi_strategy_v4.py --data data/BTCUSDT/4h/BTCUSDT-4h-merged.csv --market_type crypto --enable_plotly --plot_theme plotly_dark
python run_doji_ashi_strategy_v4.py --data data/AAPL/4h/AAPL-4h.csv --market_type stocks --market_data data/SPY/4h/SPY-4h.csv --use_resampler --max_plot_points 3000
"""

import backtrader as bt
import pandas as pd
import numpy as np
from pathlib import Path
import datetime as dt
import argparse
import sys

from strategies.doji_ashi_strategy_v4 import DojiAshiStrategyV4


def check_plotly_dependencies():
    """检查Plotly相关依赖是否可用"""
    deps = {}
    
    try:
        import plotly.graph_objects as go
        import plotly.express as px
        from plotly.subplots import make_subplots
        import plotly.offline as pyo
        deps['plotly'] = True
    except ImportError:
        deps['plotly'] = False
    
    try:
        from plotly_resampler import FigureResampler, FigureWidgetResampler
        deps['plotly_resampler'] = True
    except ImportError:
        deps['plotly_resampler'] = False
    
    return deps


def print_dependency_status():
    """打印依赖状态"""
    deps = check_plotly_dependencies()
    
    print("Visualization Dependencies Status:")
    print(f"  Plotly:           {'OK' if deps['plotly'] else 'NOT AVAILABLE'}")
    print(f"  plotly-resampler: {'OK' if deps['plotly_resampler'] else 'NOT AVAILABLE'}")
    
    if not deps['plotly']:
        print("\nWARNING: Plotly not available. Install with:")
        print("  pip install plotly")
        
    if not deps['plotly_resampler']:
        print("\nINFO: plotly-resampler not available. For better performance with large datasets, install with:")
        print("  pip install plotly-resampler")
    
    return deps


def load_csv_data(csv_path: str | Path, data_name: str = "Main") -> pd.DataFrame:
    """加载CSV数据并预处理为backtrader格式"""
    try:
        print(f"Loading {data_name} data from: {csv_path}")
        
        sample = pd.read_csv(csv_path, nrows=5)
        
        # 标准格式: open_time, open, high, low, close, volume
        if "open_time" in sample.columns:
            usecols = ["open_time", "open", "high", "low", "close", "volume"]
            df = pd.read_csv(csv_path, usecols=usecols, header=0)
            dt_index = pd.to_datetime(df.pop("open_time"), unit="ms", utc=True).dt.tz_localize(None)
            df.index = dt_index
            
        # 备选格式: datetime, open, high, low, close, volume
        elif "datetime" in sample.columns:
            df = pd.read_csv(csv_path, index_col="datetime", parse_dates=True)
            
        # Yahoo Finance格式: Date, Open, High, Low, Close, Volume
        elif "Date" in sample.columns:
            df = pd.read_csv(csv_path, index_col="Date", parse_dates=True)
            df.columns = df.columns.str.lower()
            
        else:
            raise ValueError(f"Unsupported CSV format in {csv_path}")
        
        df.index.name = "datetime"
        
        required_cols = ["open", "high", "low", "close", "volume"]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing column: {col}")
                
        df = df[required_cols].astype("float64")
        df = df.sort_index().drop_duplicates()
        
        if df.empty:
            raise ValueError("Empty dataset")
            
        if df.isnull().any().any():
            print(f"Warning: Found NaN values in {data_name} data, forward filling...")
            df = df.fillna(method='ffill').dropna()
        
        print(f"OK {data_name} data loaded: {len(df)} rows, {df.index[0]} to {df.index[-1]}")
        return df
        
    except Exception as e:
        print(f"ERROR loading {data_name} data from {csv_path}: {e}")
        raise


def setup_cerebro(initial_capital: float = 500.0, commission: float = 0.0002) -> bt.Cerebro:
    """设置Cerebro回测引擎"""
    # Numpy 2.x 兼容性补丁
    if not hasattr(np, "bool8"):
        np.bool8 = np.bool_
    
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(initial_capital)
    
    try:
        cerebro.broker.setcommission(
            commission=commission, 
            leverage=4.0, 
            commtype=bt.CommInfoBase.COMM_PERC, 
            stocklike=False
        )
    except TypeError:
        cerebro.broker.setcommission(
            commission=commission, 
            commtype=bt.CommInfoBase.COMM_PERC, 
            stocklike=False
        )
    
    return cerebro


def add_analyzers(cerebro: bt.Cerebro):
    """添加分析器"""
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trade_analysis")
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe_ratio")
    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
    cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
    
    try:
        cerebro.addanalyzer(bt.analyzers.VWR, _name="vwr")
    except:
        pass


def print_results(results, initial_value: float, final_value: float):
    """打印回测结果"""
    if not results:
        print("No results to display")
        return
        
    strat = results[0]
    
    print(f"\n{'='*60}")
    print(f"BACKTEST RESULTS")
    print(f"{'='*60}")
    
    print(f"Portfolio Performance:")
    print(f"   Initial Value: ${initial_value:,.2f}")
    print(f"   Final Value:   ${final_value:,.2f}")
    total_return = (final_value - initial_value) / initial_value * 100
    print(f"   Total Return:  {total_return:+.2f}%")
    
    # 交易分析
    try:
        trade_analysis = strat.analyzers.trade_analysis.get_analysis()
        if 'total' in trade_analysis:
            total_trades = trade_analysis['total']['total']
            if total_trades > 0:
                wins = trade_analysis.get('won', {}).get('total', 0)
                losses = trade_analysis.get('lost', {}).get('total', 0)
                win_rate = wins / total_trades * 100
                
                print(f"\nTrade Analysis:")
                print(f"   Total Trades:  {total_trades}")
                print(f"   Wins:          {wins} ({win_rate:.1f}%)")
                print(f"   Losses:        {losses}")
                
                if 'won' in trade_analysis and 'pnl' in trade_analysis['won']:
                    avg_win = trade_analysis['won']['pnl'].get('average', 0)
                    avg_loss = trade_analysis['lost']['pnl'].get('average', 0)
                    print(f"   Avg Win:       ${avg_win:.2f}")
                    print(f"   Avg Loss:      ${avg_loss:.2f}")
                    
                    if avg_loss != 0:
                        profit_factor = abs(avg_win * wins / (avg_loss * losses)) if losses > 0 else float('inf')
                        print(f"   Profit Factor: {profit_factor:.2f}")
    except Exception as e:
        print(f"Could not analyze trades: {e}")
    
    # 风险指标
    try:
        sharpe = strat.analyzers.sharpe_ratio.get_analysis().get('sharperatio', 'N/A')
        sqn = strat.analyzers.sqn.get_analysis().get('sqn', 'N/A')
        drawdown = strat.analyzers.drawdown.get_analysis()
        max_dd = drawdown.get('max', {}).get('drawdown', 'N/A')
        
        print(f"\nRisk Metrics:")
        print(f"   Sharpe Ratio:     {sharpe if sharpe != 'N/A' else 'N/A'}")
        print(f"   SQN:              {sqn if sqn != 'N/A' else 'N/A'}")
        print(f"   Max Drawdown:     {max_dd if max_dd != 'N/A' else 'N/A'}%")
        
    except Exception as e:
        print(f"Could not analyze risk metrics: {e}")


def create_fallback_plot(cerebro: bt.Cerebro, strategy_name: str = "DojiAshiV4"):
    """备选绘图方案"""
    plots_dir = Path(__file__).resolve().parent / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    
    try:
        from backtrader_plotting import Bokeh
        
        html_filename = plots_dir / f"{strategy_name.lower()}_{ts}.html"
        b = Bokeh(
            plot_mode="single",
            output_mode="save", 
            filename=str(html_filename),
            show=False
        )
        cerebro.plot(b)
        print(f"Fallback Bokeh plot saved: {html_filename}")
        
        try:
            import webbrowser
            webbrowser.open(f'file://{html_filename.absolute()}')
            print(f"Opening plot in browser...")
        except:
            print(f"Please manually open: {html_filename}")
            
    except Exception as e:
        print(f"Bokeh plotting error: {e}")
        
        try:
            print("Falling back to matplotlib...")
            fig_path = plots_dir / f"{strategy_name.lower()}_{ts}.png"
            cerebro.plot(savefig=dict(fname=str(fig_path), dpi=150))
            print(f"Static plot saved: {fig_path}")
        except Exception as e2:
            print(f"Matplotlib fallback also failed: {e2}")


def main():
    parser = argparse.ArgumentParser(
        description="Doji Ashi Strategy v4 Backtest Runner with Advanced Plotly Visualization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic crypto backtest with Plotly
  python run_doji_ashi_strategy_v4.py --data data/BTCUSDT/4h/BTCUSDT-4h-merged.csv --market_type crypto --enable_plotly
  
  # Advanced visualization with resampler for large datasets
  python run_doji_ashi_strategy_v4.py --data data/BTCUSDT/4h/BTCUSDT-4h-merged.csv --market_type crypto --enable_plotly --use_resampler --max_plot_points 3000
  
  # Stocks mode with market data and custom theme
  python run_doji_ashi_strategy_v4.py --data data/AAPL/1h/AAPL-1h.csv --market_type stocks --market_data data/SPY/1h/SPY-1h.csv --plot_theme plotly_white
  
  # Disable Plotly and use fallback plotting
  python run_doji_ashi_strategy_v4.py --data data.csv --no_plotly --use_fallback_plot
        """
    )
    
    # 数据参数
    parser.add_argument('--data', type=str,
                       help='Path to main trading data CSV file')
    parser.add_argument('--daily_data', type=str, 
                       help='Path to daily timeframe CSV (optional)')
    parser.add_argument('--market_data', type=str,
                       help='Path to market index CSV (SPY/BTC, required for market filters)')
    
    # 策略参数
    parser.add_argument('--market_type', type=str, default='crypto', choices=['stocks', 'crypto'],
                       help='Market type preset (default: crypto)')
    parser.add_argument('--direction', type=str, default='long', choices=['long', 'short', 'both'],
                       help='Trade direction (default: both)')
    parser.add_argument('--filters', type=str, default='daily,trigger',
                       help='Comma-separated list of filters: daily,trigger,market,rs,volume,vwap,time')
    
    # 回测参数
    parser.add_argument('--capital', type=float, default=500.0,
                       help='Initial capital (default: 500)')
    parser.add_argument('--commission', type=float, default=0.0002,
                       help='Commission rate (default: 0.0002 = 0.02%%)')
    
    # 风险参数
    parser.add_argument('--atr_mult', type=float, default=1.5,
                       help='ATR multiplier for stop loss (default: 1.5)')
    parser.add_argument('--risk_reward', type=float, default=2.0,
                       help='Risk reward ratio (default: 2.0)')
    parser.add_argument('--position_pct', type=float, default=0.20,
                       help='Position size as percentage of equity (default: 0.20)')
    
    # === PLOTLY 可视化参数 === #
    parser.add_argument('--enable_plotly', action='store_true', default=True,
                       help='Enable advanced Plotly visualization (default: True)')
    parser.add_argument('--no_plotly', action='store_true',
                       help='Disable Plotly visualization')
    parser.add_argument('--use_resampler', action='store_true', default=True,
                       help='Use plotly-resampler for large datasets (default: True)')
    parser.add_argument('--no_resampler', action='store_true',
                       help='Disable plotly-resampler')
    parser.add_argument('--max_plot_points', type=int, default=5000,
                       help='Maximum plot points before using resampler (default: 5000)')
    parser.add_argument('--plot_theme', type=str, default='plotly_dark',
                       choices=['plotly', 'plotly_white', 'plotly_dark', 'ggplot2', 'seaborn', 'simple_white'],
                       help='Plotly theme (default: plotly_dark)')
    parser.add_argument('--plot_save_path', type=str, default='plots',
                       help='Directory to save plots (default: plots)')
    
    # 绘图内容控制
    parser.add_argument('--no_indicators', action='store_true',
                       help='Disable technical indicators in plot')
    parser.add_argument('--no_signals', action='store_true',
                       help='Disable trade signals in plot')
    parser.add_argument('--no_volume', action='store_true',
                       help='Disable volume subplot')
    
    # 输出参数
    parser.add_argument('--use_fallback_plot', action='store_true',
                       help='Use fallback plotting (Bokeh/matplotlib) if Plotly fails')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--check_deps', action='store_true',
                       help='Check dependencies and exit')
    
    args = parser.parse_args()
    
    # 检查依赖并退出（如果请求）
    if args.check_deps:
        deps = print_dependency_status()
        return
    
    # 检查必需的data参数
    if not args.data:
        parser.error("the following arguments are required: --data")
    
    print(f"\n>> Starting Doji Ashi Strategy v4 Backtest (Advanced Plotly Edition)")
    print(f"{'='*70}")
    
    # 检查Plotly依赖
    deps = check_plotly_dependencies()
    if args.verbose:
        print_dependency_status()
    
    # 处理可视化参数
    enable_plotly = args.enable_plotly and not args.no_plotly and deps['plotly']
    use_resampler = args.use_resampler and not args.no_resampler and deps['plotly_resampler'] and enable_plotly
    
    if args.enable_plotly and not deps['plotly']:
        print("WARNING: Plotly requested but not available. Using fallback plotting.")
        enable_plotly = False
    
    try:
        # 设置Cerebro
        cerebro = setup_cerebro(args.capital, args.commission)
        
        # 加载主要数据
        base_dir = Path(__file__).resolve().parent
        main_data_path = Path(args.data) if Path(args.data).is_absolute() else Path(args.data)
        df_main = load_csv_data(main_data_path, "Main")
        
        # 创建主要数据feed
        main_feed = bt.feeds.PandasData(
            dataname=df_main,
            timeframe=bt.TimeFrame.Minutes,
            compression=240,
            name="main"
        )
        cerebro.adddata(main_feed)
        
        # 创建日线数据feed
        if args.daily_data:
            daily_data_path = Path(args.daily_data) if Path(args.daily_data).is_absolute() else Path(args.daily_data)
            df_daily = load_csv_data(daily_data_path, "Daily")
            daily_feed = bt.feeds.PandasData(dataname=df_daily, name="daily")
            cerebro.adddata(daily_feed)
        else:
            daily_feed = cerebro.resampledata(main_feed, timeframe=bt.TimeFrame.Days, compression=1)
        
        # 创建市场数据feed（如果提供）
        if args.market_data:
            market_data_path = Path(args.market_data) if Path(args.market_data).is_absolute() else Path(args.market_data)
            df_market = load_csv_data(market_data_path, "Market")
            market_feed = bt.feeds.PandasData(dataname=df_market, name="market")
            cerebro.adddata(market_feed)
        
        # 解析过滤器
        enabled_filters = [f.strip().lower() for f in args.filters.split(',')]
        
        # 策略配置
        strategy_params = dict(
            # 基础设置
            market_type=args.market_type,
            trade_direction=args.direction.lower(),
            
            # 过滤器开关
            enable_daily_trend_filter='daily' in enabled_filters,
            enable_entry_trigger='trigger' in enabled_filters,
            enable_market_filter_input='market' in enabled_filters,
            enable_relative_strength='rs' in enabled_filters,
            enable_volume_filter='volume' in enabled_filters,
            enable_vwap_filter_entry='vwap' in enabled_filters,
            enable_time_filter='time' in enabled_filters,
            
            # 风险参数
            atr_multiplier=args.atr_mult,
            risk_reward_ratio=args.risk_reward,
            order_percent=args.position_pct,
            
            # === PLOTLY 可视化参数 === #
            enable_plotly=enable_plotly,
            use_resampler=use_resampler,
            plot_indicators=not args.no_indicators,
            plot_signals=not args.no_signals,
            plot_volume=not args.no_volume,
            plot_save_path=args.plot_save_path,
            plot_theme=args.plot_theme,
            max_plot_points=args.max_plot_points,
            
            # 其他设置 - 按用户要求只使用ATR退出
            use_time_exit=False,  # 禁用时间退出
            max_bars_in_trade=100,
            cooldown_bars=10,
            warmup_daily=200,
        )
        
        if args.verbose:
            print(f"\nStrategy Configuration:")
            for key, value in strategy_params.items():
                print(f"   {key}: {value}")
            
            print(f"\nVisualization Settings:")
            print(f"   Plotly Enabled: {enable_plotly}")
            print(f"   Resampler: {use_resampler}")
            print(f"   Theme: {args.plot_theme}")
            print(f"   Max Points: {args.max_plot_points}")
        
        # 添加策略
        cerebro.addstrategy(DojiAshiStrategyV4, **strategy_params)
        
        # 添加分析器
        add_analyzers(cerebro)
        
        # 运行回测
        print(f"\nRunning backtest...")
        initial_value = cerebro.broker.getvalue()
        print(f"Starting Portfolio Value: ${initial_value:,.2f}")
        
        results = cerebro.run()
        final_value = cerebro.broker.getvalue()
        
        # 打印结果
        print_results(results, initial_value, final_value)
        
        # 可视化处理
        if enable_plotly:
            print(f"\nCreating advanced Plotly visualization...")
            # Plotly图表由策略在stop()方法中自动创建和保存
        elif args.use_fallback_plot:
            print(f"\nCreating fallback plot...")
            create_fallback_plot(cerebro, f"DojiAshiV4_{args.market_type}")
        else:
            print(f"\nSkipping plot creation (use --use_fallback_plot for basic charts)")
        
        print(f"\nBacktest completed successfully!")
        
        if enable_plotly:
            print(f"\nNOTE: Advanced Plotly chart with the following features:")
            print(f"  - Interactive candlestick chart with technical indicators")
            print(f"  - Trade signals visualization")
            print(f"  - Volume and portfolio value subplots")
            print(f"  - Responsive design with zoom and pan capabilities")
            if use_resampler:
                print(f"  - Optimized for large datasets using plotly-resampler")
        
    except KeyboardInterrupt:
        print(f"\nBacktest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nBacktest failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
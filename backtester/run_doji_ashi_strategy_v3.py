"""
Doji Ashi Strategy v3 运行脚本
支持多重过滤器、市场类型预设、多时间框架数据

使用方法:
python run_doji_ashi_strategy_v3.py --data data/BTCUSDT/4h/BTCUSDT-4h-merged.csv --market_type crypto
python run_doji_ashi_strategy_v3.py --data data/AAPL/4h/AAPL-4h.csv --market_type stocks --market_data data/SPY/4h/SPY-4h.csv
"""

import backtrader as bt
import pandas as pd
import numpy as np
from pathlib import Path
import datetime as dt
import argparse
import sys

from strategies.doji_ashi_strategy_v3 import DojiAshiStrategyV3


def load_csv_data(csv_path: str | Path, data_name: str = "Main") -> pd.DataFrame:
    """
    加载CSV数据并预处理为backtrader格式
    
    Args:
        csv_path: CSV文件路径
        data_name: 数据名称（用于日志）
    
    Returns:
        处理后的DataFrame
    """
    try:
        print(f"Loading {data_name} data from: {csv_path}")
        
        # 尝试检测CSV格式
        sample = pd.read_csv(csv_path, nrows=5)
        
        # 标准格式: open_time, open, high, low, close, volume
        if "open_time" in sample.columns:
            usecols = ["open_time", "open", "high", "low", "close", "volume"]
            df = pd.read_csv(csv_path, usecols=usecols, header=0)
            
            # 转换毫秒时间戳
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
        
        # 确保数据类型和质量
        required_cols = ["open", "high", "low", "close", "volume"]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing column: {col}")
                
        df = df[required_cols].astype("float64")
        df = df.sort_index().drop_duplicates()
        
        # 数据质量检查
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
    """
    设置Cerebro回测引擎
    
    Args:
        initial_capital: 初始资金
        commission: 手续费率
    
    Returns:
        配置好的Cerebro实例
    """
    # Numpy 2.x 兼容性补丁
    if not hasattr(np, "bool8"):
        np.bool8 = np.bool_
    
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(initial_capital)
    
    # 设置佣金和杠杆
    try:
        cerebro.broker.setcommission(
            commission=commission, 
            leverage=4.0, 
            commtype=bt.CommInfoBase.COMM_PERC, 
            stocklike=False
        )
    except TypeError:
        # 旧版本backtrader不支持leverage参数
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
    
    # Kelly Criterion analyzer (如果可用)
    try:
        cerebro.addanalyzer(bt.analyzers.VWR, _name="vwr")  # Variability-Weighted Return
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


def create_plot(cerebro: bt.Cerebro, strategy_name: str = "DojiAshiV3"):
    """创建交互式图表"""
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
        print(f"Interactive plot saved: {html_filename}")
        
        # 尝试自动打开浏览器
        try:
            import webbrowser
            webbrowser.open(f'file://{html_filename.absolute()}')
            print(f"Opening plot in browser...")
        except:
            print(f"Please manually open: {html_filename}")
            
    except Exception as e:
        print(f"Bokeh plotting error: {e}")
        
        # 备选方案：matplotlib
        try:
            print("Falling back to matplotlib...")
            fig_path = plots_dir / f"{strategy_name.lower()}_{ts}.png"
            cerebro.plot(savefig=dict(fname=str(fig_path), dpi=150))
            print(f"Static plot saved: {fig_path}")
        except Exception as e2:
            print(f"Matplotlib fallback also failed: {e2}")


def main():
    parser = argparse.ArgumentParser(
        description="Doji Ashi Strategy v3 Backtest Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Crypto mode with BTC market filter
  python run_doji_ashi_strategy_v3.py --data data/BTCUSDT/4h/BTCUSDT-4h-merged.csv --market_type crypto
  
  # Stocks mode with SPY market data
  python run_doji_ashi_strategy_v3.py --data data/AAPL/1h/AAPL-1h.csv --market_type stocks --market_data data/SPY/1h/SPY-1h.csv
  
  # Custom configuration
  python run_doji_ashi_strategy_v3.py --data data.csv --direction long --filters daily,volume,vwap
        """
    )
    
    # 数据参数
    parser.add_argument('--data', type=str, required=True,
                       help='Path to main trading data CSV file')
    parser.add_argument('--daily_data', type=str, 
                       help='Path to daily timeframe CSV (optional, will resample from main if not provided)')
    parser.add_argument('--market_data', type=str,
                       help='Path to market index CSV (SPY/BTC, required for market filters)')
    
    # 策略参数
    parser.add_argument('--market_type', type=str, default='crypto', choices=['stocks', 'crypto'],
                       help='Market type preset (default: crypto)')
    parser.add_argument('--direction', type=str, default='both', choices=['long', 'short', 'both'],
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
    
    # 输出参数
    parser.add_argument('--no_plot', action='store_true',
                       help='Skip plotting')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    print(f"\n>> Starting Doji Ashi Strategy v3 Backtest")
    print(f"{'='*50}")
    
    try:
        # 设置Cerebro
        cerebro = setup_cerebro(args.capital, args.commission)
        
        # 加载主要数据
        base_dir = Path(__file__).resolve().parent
        main_data_path = Path(args.data) if Path(args.data).is_absolute() else base_dir / args.data
        df_main = load_csv_data(main_data_path, "Main")
        
        # 创建主要数据feed
        main_feed = bt.feeds.PandasData(
            dataname=df_main,
            timeframe=bt.TimeFrame.Minutes,
            compression=240,  # 假设4小时数据
            name="main"
        )
        cerebro.adddata(main_feed)
        
        # 创建日线数据feed
        if args.daily_data:
            daily_data_path = Path(args.daily_data) if Path(args.daily_data).is_absolute() else base_dir / args.daily_data
            df_daily = load_csv_data(daily_data_path, "Daily")
            daily_feed = bt.feeds.PandasData(dataname=df_daily, name="daily")
            cerebro.adddata(daily_feed)
        else:
            # 从主数据重新采样日线
            daily_feed = cerebro.resampledata(main_feed, timeframe=bt.TimeFrame.Days, compression=1)
        
        # 创建市场数据feed（如果提供）
        if args.market_data:
            market_data_path = Path(args.market_data) if Path(args.market_data).is_absolute() else base_dir / args.market_data
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
            
            # 其他设置
            use_time_exit=True,
            max_bars_in_trade=100,
            cooldown_bars=10,
            warmup_daily=200,
        )
        
        if args.verbose:
            print(f"\nStrategy Configuration:")
            for key, value in strategy_params.items():
                print(f"   {key}: {value}")
        
        # 添加策略
        cerebro.addstrategy(DojiAshiStrategyV3, **strategy_params)
        
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
        
        # 创建图表
        if not args.no_plot:
            create_plot(cerebro, f"DojiAshiV3_{args.market_type}")
        
        print(f"\nBacktest completed successfully!")
        
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
import backtrader as bt
import pandas as pd
import numpy as np
from pathlib import Path
import datetime as dt

from strategies.doji_ashi_strategy_v2 import DojiAshiStrategyV2

def load_csv(csv_path: str | Path) -> pd.DataFrame:
    """
    从 CSV 文件加载市场数据，将 'open_time'（毫秒）转换为
    一个无时区的 datetime 索引，并确保数据格式正确。

    Args:
        csv_path: CSV 文件的路径。

    Returns:
        一个为 backtrader 准备好的、带有无时区索引的 DataFrame。
    """
    usecols = ["open_time", "open", "high", "low", "close", "volume"]
    df = pd.read_csv(csv_path, usecols=usecols, header=0)
    
    # 将毫秒时间戳转换为无时区的 datetime 索引
    dt_index = pd.to_datetime(df.pop("open_time"), unit="ms", utc=True).dt.tz_localize(None)
    df.index = dt_index
    df.index.name = "datetime"

    # 确保数据类型正确，排序并去重
    df = df.astype("float64").sort_index().drop_duplicates()
    return df

def main():
    # Numpy 2.x 兼容性补丁
    if not hasattr(np, "bool8"):
        np.bool8 = np.bool_

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(500.0)
    
    # 设置佣金和杠杆
    try:
        cerebro.broker.setcommission(
            commission=0.0002, leverage=4.0, commtype=bt.CommInfoBase.COMM_PERC, stocklike=False
        )
    except TypeError:
        cerebro.broker.setcommission(commission=0.0002, commtype=bt.CommInfoBase.COMM_PERC, stocklike=False)

    # --- 数据加载 ---
    base_dir = Path(__file__).resolve().parent
    path4h = base_dir / "data" / "BTCUSDT" / "4h" / "BTCUSDT-4h-merged.csv"
    
    # 使用新的加载函数
    df4h = load_csv(path4h)
    
    data4h = bt.feeds.PandasData(
        dataname=df4h,
        timeframe=bt.TimeFrame.Minutes,
        compression=240,  # 4 hours
    )

    cerebro.adddata(data4h)
    cerebro.resampledata(data4h, timeframe=bt.TimeFrame.Days, compression=1)

    # --- 策略配置 ---
    cerebro.addstrategy(
        DojiAshiStrategyV2,
        trade_direction="long",
        enable_vwap_filter_entry=False,
        enable_volume_filter=True,
        use_time_exit=True,
        max_bars_in_trade=100,
        maker_mode=True,
        maker_limit_offset_percent=0.02,
        size_step=0.001,
        leverage=4.0,
        warmup_daily=200,
        pending_order_timeout_bars=10,
    )

    # --- 分析器 ---
    print(f"Starting Portfolio Value: {cerebro.broker.getvalue():.2f}")
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe")
    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="dd")

    # --- 运行回测 ---
    result = cerebro.run()
    print(f"Final Portfolio Value:   {cerebro.broker.getvalue():.2f}")
    
    # --- 打印分析结果 ---
    try:
        strat = result[0]
        print("\n=== Results ===")
        print("TradeAnalyzer:", strat.analyzers.ta.get_analysis())
        print("Sharpe:", strat.analyzers.sharpe.get_analysis())
        print("SQN:", strat.analyzers.sqn.get_analysis())
        print("DrawDown:", strat.analyzers.dd.get_analysis())
    except Exception as e:
        print(f"Could not print analyzer results: {e}")

    # --- 绘图 ---
    plots_dir = Path(__file__).resolve().parent / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.utcnow().strftime('%Y%m%d_%H%M%S')

    try:
        from backtrader_plotting import Bokeh
        from backtrader_plotting.schemes import Tradimo

        html_filename = plots_dir / f"doji_ashi_strategy_v2_{ts}.html"
        b = Bokeh(
            plot_mode="single",
            output_mode="save",
            filename=str(html_filename),
            scheme=Tradimo(),
            show=False
        )
        cerebro.plot(b)
        print(f"Bokeh plot saved to: {html_filename}")
    except Exception as be:
        print(f"Bokeh plot error: {be}")

if __name__ == "__main__":
    main()
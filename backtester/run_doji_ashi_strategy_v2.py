import backtrader as bt
import pandas as pd
import numpy as np
import importlib.util as _impspec
from pathlib import Path
import datetime as dt

from strategies.doji_ashi_strategy_v2 import DojiAshiStrategyV2


class PandasData(bt.feeds.PandasData):
    params = (
        ("datetime", None),
        ("open", -1),
        ("high", -1),
        ("low", -1),
        ("close", -1),
        ("volume", -1),
        ("openinterest", -1),
    )


def _parse_epoch_series_to_datetime_ms_first(epoch_series: pd.Series) -> pd.DatetimeIndex:
    """尝试按毫秒解析，失败则回退到微秒/秒，返回 naive UTC DatetimeIndex。"""
    for unit in ("ms", "us", "s"):
        try:
            dt = pd.to_datetime(epoch_series, unit=unit, utc=True)
            # Series 使用 .dt；Index 直接方法
            if hasattr(dt, "dt"):
                dt = dt.dt.tz_convert("UTC").dt.tz_localize(None)
            else:
                dt = dt.tz_convert("UTC").tz_localize(None)
            return dt
        except Exception:
            continue
    # 最后兜底
    dt = pd.to_datetime(epoch_series, utc=True, errors="coerce")
    if hasattr(dt, "dt"):
        return dt.dt.tz_convert("UTC").dt.tz_localize(None)
    return dt.tz_convert("UTC").tz_localize(None)


def load_binance_csv_to_pandas(csv_path: str) -> pd.DataFrame:
    names = [
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "x",
        "x2",
        "x3",
        "x4",
        "x5",
        "x6",
    ]
    df = pd.read_csv(csv_path, header=None, names=names, usecols=[0, 1, 2, 3, 4, 5])
    # 自适应时间戳解析 -> naive UTC datetime 作为索引
    df.index = _parse_epoch_series_to_datetime_ms_first(df["open_time"]) 
    df = df.drop(columns=["open_time"]).copy()
    df["openinterest"] = 0.0
    return df[["open", "high", "low", "close", "volume", "openinterest"]]


def main():
    # Numpy 2.x 兼容：某些绘图库仍使用 np.bool8 名称
    if not hasattr(np, "bool8"):
        np.bool8 = np.bool_

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10000.0)
    # 标准化的百分比佣金设置；新版本支持 leverage，旧版本退化为 margin
    try:
        cerebro.broker.setcommission(
            commission=0.0005,
            leverage=1.0,
            commtype=bt.CommInfoBase.COMM_PERC,
            stocklike=False,
        )
    except TypeError:
        cerebro.broker.setcommission(
            commission=0.0005,
            margin=1.0,
            commtype=bt.CommInfoBase.COMM_PERC,
            stocklike=False,
        )

    # Use project-relative data path instead of hardcoded absolute path
    base_dir = Path(__file__).resolve().parent
    path4h = base_dir / "data" / "BTCUSDT" / "4h" / "BTCUSDT-4h-merged.csv"

    df4h = load_binance_csv_to_pandas(str(path4h))

    data4h = bt.feeds.PandasData(dataname=df4h, timeframe=bt.TimeFrame.Minutes, compression=240)

    # datas[0] = 4h 主数据
    cerebro.adddata(data4h)
    # datas[1] = 由 data0 重采样得到的 1d 日线，避免多 CSV 带来的错位；不使用 cheat_on_open
    cerebro.resampledata(data4h, timeframe=bt.TimeFrame.Days, compression=1)

    cerebro.addstrategy(
        DojiAshiStrategyV2,
        enable_vwap_filter_entry=False,
        enable_volume_filter=True,
        use_time_exit=True,
        max_bars_in_trade=100,
        # --- maker/尺寸/暖启动/超时 设置 ---
        maker_mode=True,
        maker_limit_offset_percent=0.02,   # 0.02% 轻微偏移，减少“立刻成交”的概率
        size_step=0.001,                   # 交易所步进，例如合约/现货最小数量步进
        leverage=1.0,                      # 与 broker 一致；若 broker 已设置杠杆，这里保持 1.0
        warmup_daily=200,
        pending_order_timeout_bars=10,     # 限价未成交超时撤单
    )

    print(f"Starting Portfolio Value: {cerebro.broker.getvalue():.2f}")
    # 分析器（来自 vchatgpt5 Runner 的实用集合）
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe")
    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="dd")
    cerebro.addanalyzer(bt.analyzers.TimeReturn, _name="tr")

    result = cerebro.run()
    strat = result[0]
    print(f"Final Portfolio Value:   {cerebro.broker.getvalue():.2f}")
    try:
        print("\n=== Results ===")
        print("TradeAnalyzer:", strat.analyzers.ta.get_analysis())
        print("Sharpe:", strat.analyzers.sharpe.get_analysis())
        print("SQN:", strat.analyzers.sqn.get_analysis())
        print("DrawDown:", strat.analyzers.dd.get_analysis())
        tr_items = list(strat.analyzers.tr.get_analysis().items())
        print("TimeReturn (first 5):", tr_items[:5])
    except Exception as _:
        pass

    # 优先使用 backtrader_plotting → 失败则保存 matplotlib PNG
    plots_dir = Path(__file__).resolve().parent / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.utcnow().strftime('%Y%m%d_%H%M%S')

    try:
        if _impspec.find_spec("backtrader_plotting") is not None:
            try:
                from backtrader_plotting import Bokeh
                from backtrader_plotting.schemes import Tradimo

                html_path = plots_dir / f"doji_ashi_strategy_v2_{ts}.html"
                b = Bokeh(style="candlestick", plot_mode="single", scheme=Tradimo(), filename=str(html_path))
                cerebro.plot(b)
                print(f"Interactive plot saved to: {html_path}")
                return
            except Exception as be:
                print(f"Bokeh plot error, fallback to matplotlib: {be}")

        # fallback to matplotlib
        figs = cerebro.plot(style="candlestick")
        try:
            import matplotlib
            import matplotlib.pyplot as plt  # noqa: F401
            idx = 0
            for fset in figs:
                for fig in fset:
                    png_path = plots_dir / f"doji_ashi_strategy_v2_{ts}_{idx}.png"
                    fig.savefig(str(png_path), dpi=150, bbox_inches='tight')
                    idx += 1
            print(f"Matplotlib plots saved to: {plots_dir}")
        except Exception as se:
            print(f"Matplotlib save error: {se}")
    except Exception as e:
        print(f"Plot error: {e}")


if __name__ == "__main__":
    main()



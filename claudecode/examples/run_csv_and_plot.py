# -*- coding: utf-8 -*-
import argparse
import pandas as pd
from pathlib import Path
from viz.plotly_bt import make_figure

def _read_csv_auto(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # 兼容 Binance / Yahoo 常见列
    # Binance 4h/1h 等 K线常见列：open_time, open, high, low, close, volume, close_time, ...
    # Yahoo：Datetime, Open, High, Low, Close, Volume, ...
    # 其余列不影响绘图
    return df

def _read_trades_optional(path: str | None) -> pd.DataFrame | None:
    if not path: return None
    p = Path(path)
    if not p.exists(): return None
    t = pd.read_csv(p)
    return t

def _read_equity_optional(path: str | None) -> pd.Series | None:
    if not path: return None
    p = Path(path)
    if not p.exists(): return None
    df = pd.read_csv(p)
    # 允许列名为 equity/value 或取第一列
    if "equity" in df.columns: s = df["equity"]
    elif "value" in df.columns: s = df["value"]
    else:
        # 尝试第一列为值，第一列或名为 datetime 的列做索引
        valcol = [c for c in df.columns if c.lower() not in ("datetime","date","time","timestamp")]
        valcol = valcol[0] if valcol else df.columns[0]
        s = df[valcol]
    # 设索引
    dtcol = None
    for k in ["datetime","date","time","timestamp"]:
        if k in [c.lower() for c in df.columns]:
            dtcol = [c for c in df.columns if c.lower()==k][0]
            break
    if dtcol:
        s.index = pd.to_datetime(df[dtcol], utc=True, errors="coerce")
        s.index = s.index.tz_convert(None)
    return s

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Plot interactive chart from OHLCV CSV (+ optional trades/equity).")
    ap.add_argument("--csv", required=True, help="OHLCV CSV 文件路径（需含 open/high/low/close，时间列支持 datetime/date/timestamp/open_time）")
    ap.add_argument("--trades", default=None, help="可选：交易明细 CSV（需含 datetime 与 price；可选 side/size/pnl）")
    ap.add_argument("--equity", default=None, help="可选：资金曲线 CSV（可含 datetime + equity/value）")
    ap.add_argument("--out", default="reports/demo_plot.html", help="输出 HTML 路径")
    ap.add_argument("--title", default=None, help="图表标题")
    args = ap.parse_args()

    df = _read_csv_auto(args.csv)
    tdf = _read_trades_optional(args.trades)
    eq  = _read_equity_optional(args.equity)

    fig = make_figure(df, trades=tdf, equity=eq, title=args.title, out_html=args.out)
    print(f"已生成：{args.out}")

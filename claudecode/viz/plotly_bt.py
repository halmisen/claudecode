# -*- coding: utf-8 -*-
from __future__ import annotations
import os
import math
import pandas as pd
from typing import Optional, Union
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def _ensure_dt_index(df: pd.DataFrame) -> pd.DataFrame:
    cand_cols = {c.lower(): c for c in df.columns}
    # 常见时间列名自动识别
    for k in ["datetime", "date", "time", "timestamp", "open_time"]:
        if k in cand_cols:
            col = cand_cols[k]
            s = pd.to_datetime(df[col], utc=True, errors="coerce")
            # 去 tz（Plotly 不强制要求 tz-aware）
            s = s.dt.tz_convert(None) if getattr(s.dt, "tz", None) is not None else s
            df = df.copy()
            df.index = s
            if col != "datetime":
                df = df.rename(columns={col: "datetime"})
            break
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("无法识别时间列：需要 datetime/date/timestamp/open_time 其一。")
    return df

def _normalize_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    # 归一化列名到 open/high/low/close/volume
    mapper = {}
    lower = {c.lower(): c for c in df.columns}
    for target, candidates in {
        "open": ["open", "o"],
        "high": ["high", "h"],
        "low":  ["low", "l"],
        "close":["close", "c"],
        "volume":["volume", "vol", "v"]
    }.items():
        for cand in candidates:
            if cand in lower:
                mapper[lower[cand]] = target
                break
    out = df.rename(columns=mapper)
    for k in ["open","high","low","close"]:
        if k not in out.columns:
            raise ValueError(f"缺少列：{k}")
    if "volume" not in out.columns:
        out["volume"] = 0.0
    return out[["open","high","low","close","volume"]]

def make_figure(
    candles: pd.DataFrame,
    trades: Optional[pd.DataFrame] = None,
    equity: Optional[Union[pd.Series, pd.DataFrame]] = None,
    title: Optional[str] = None,
    out_html: Optional[str] = None
) -> go.Figure:
    """生成交互式图表：上方K线含买卖标记，下方资金曲线与成交量"""
    df = _ensure_dt_index(candles)
    df = _normalize_ohlcv(df).sort_index()

    # 统一长度（防止不同索引导致 hover 对不齐）
    eq = None
    if equity is not None:
        eq = equity.copy()
        if isinstance(eq, pd.DataFrame):
            # 取第一列或名为 'equity'/'value' 的列
            if "equity" in eq.columns: eq = eq["equity"]
            elif "value" in eq.columns: eq = eq["value"]
            else: eq = eq.iloc[:,0]
        eq.index = pd.to_datetime(eq.index, utc=True, errors="coerce").tz_convert(None)
        eq = eq.sort_index().reindex(df.index, method="pad")

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.72, 0.28],
        specs=[[{"secondary_y": False}],
               [{"secondary_y": True}]]
    )

    # K线
    fig.add_trace(
        go.Candlestick(
            x=df.index, open=df["open"], high=df["high"],
            low=df["low"], close=df["close"], name="OHLC",
            increasing_line_width=1, decreasing_line_width=1
        ),
        row=1, col=1
    )

    # 成交量（下方左轴）
    fig.add_trace(
        go.Bar(x=df.index, y=df["volume"], name="Volume", opacity=0.3),
        row=2, col=1, secondary_y=False
    )

    # 资金曲线（下方右轴）
    if eq is not None:
        fig.add_trace(
            go.Scatter(x=eq.index, y=eq.values, mode="lines", name="Equity"),
            row=2, col=1, secondary_y=True
        )

    # 交易标记
    if trades is not None and len(trades) > 0:
        tdf = trades.copy()
        # 规范列名
        cols = {c.lower(): c for c in tdf.columns}
        # 必需：时间+价格；可选：side/size/pnl
        dtcol = cols.get("datetime") or cols.get("date") or cols.get("time") or cols.get("timestamp")
        pcol  = cols.get("price") or cols.get("avg_price") or cols.get("fill_price")
        scol  = cols.get("side") if "side" in cols else None
        sizec = cols.get("size") or cols.get("qty") or cols.get("quantity")
        pnlc  = cols.get("pnl") or cols.get("pl") or cols.get("profit")
        if not dtcol or not pcol:
            raise ValueError("trades 需要至少包含 [datetime, price] 两列。")
        tdf["__dt__"] = pd.to_datetime(tdf[dtcol], utc=True, errors="coerce").dt.tz_convert(None)
        tdf["__p__"] = pd.to_numeric(tdf[pcol], errors="coerce")
        if scol:
            s = tdf[scol].astype(str).str.lower()
            buy = tdf[s.str.startswith("b")]
            sell = tdf[s.str.startswith("s")]
        else:
            # 没有 side 列则全部当作 buy/sell 混合点，仅作标记
            buy = tdf.iloc[::2]  # 偶数位买
            sell = tdf.iloc[1::2]  # 奇数位卖
        # Buy
        fig.add_trace(
            go.Scatter(
                x=buy["__dt__"], y=buy["__p__"], mode="markers",
                marker_symbol="triangle-up", marker_size=10,
                name="Buy",
                text=[f"size={buy[sizec].iloc[i]}" if sizec else "" for i in range(len(buy))],
                hovertemplate="Buy<br>%{x}<br>%{y}<extra></extra>",
            ),
            row=1, col=1
        )
        # Sell
        fig.add_trace(
            go.Scatter(
                x=sell["__dt__"], y=sell["__p__"], mode="markers",
                marker_symbol="triangle-down", marker_size=10,
                name="Sell",
                text=[f"size={sell[sizec].iloc[i]}" if sizec else "" for i in range(len(sell))],
                hovertemplate="Sell<br>%{x}<br>%{y}<extra></extra>",
            ),
            row=1, col=1
        )

    fig.update_layout(
        title=title or "Backtest Interactive Chart",
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
        legend_orientation="h",
        margin=dict(l=20, r=20, t=40, b=20),
    )
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1, secondary_y=False)
    if eq is not None:
        fig.update_yaxes(title_text="Equity", row=2, col=1, secondary_y=True)

    if out_html:
        os.makedirs(os.path.dirname(out_html), exist_ok=True)
        fig.write_html(out_html, include_plotlyjs="cdn", auto_open=False)
    return fig

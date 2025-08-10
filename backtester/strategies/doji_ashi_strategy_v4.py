"""
Doji Ashi Strategy v4 - 集成Plotly绘图的增强版本
基于 v3 版本，添加了高级 Plotly + plotly-resampler 交互式可视化功能

主要新功能:
- 集成 Plotly 交互式图表
- plotly-resampler 大数据集性能优化
- 详细的指标和交易信号可视化
- 自定义图表样式和布局
- 多时间框架数据展示

Source Reference: pinescript/strategies/reversal/Doji_Ashi_Strategy_v2.6.pine
Enhanced with: Advanced Plotly Visualization
"""

from __future__ import annotations

# --- Standard Library ---
import datetime
from typing import Optional, Dict, List, Any
import os
from pathlib import Path

# --- Core Scientific ---
import numpy as np
import pandas as pd

# Optional scientific (guarded)
try:
    from scipy import stats  # noqa: F401
except Exception:
    stats = None

# --- Backtesting ---
import backtrader as bt
import backtrader.indicators as btind

# TA-Lib (installed in venv) and Backtrader-TALIB bridge
try:
    import talib  # noqa: F401
    HAS_TALIB = True
except Exception:
    talib = None
    HAS_TALIB = False

# pandas_ta: optional
try:
    import pandas_ta as ta  # noqa: F401
    HAS_PANDAS_TA = True
except Exception:
    ta = None
    HAS_PANDAS_TA = False

# --- Data & HTTP (optional) ---
try:
    import requests  # noqa: F401
    HAS_REQUESTS = True
except Exception:
    requests = None
    HAS_REQUESTS = False

try:
    import yfinance as yf  # noqa: F401
    HAS_YFINANCE = True
except Exception:
    yf = None
    HAS_YFINANCE = False

# --- Visualization (Enhanced Plotly Support) ---
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    HAS_PLOTLY = True
except Exception:
    go = None
    px = None
    make_subplots = None
    pyo = None
    HAS_PLOTLY = False

try:
    from plotly_resampler import FigureResampler, FigureWidgetResampler
    HAS_PLOTLY_RESAMPLER = True
except Exception:
    FigureResampler = None
    FigureWidgetResampler = None
    HAS_PLOTLY_RESAMPLER = False

# --- Traditional Visualization (optional) ---
try:
    import matplotlib.pyplot as plt  # noqa: F401
    HAS_MATPLOTLIB = True
except Exception:
    plt = None
    HAS_MATPLOTLIB = False

try:
    import seaborn as sns  # noqa: F401
    HAS_SEABORN = True
except Exception:
    sns = None
    HAS_SEABORN = False

# --- Performance & Utilities (optional) ---
try:
    from numba import jit  # noqa: F401
    HAS_NUMBA = True
except Exception:
    jit = None
    HAS_NUMBA = False

try:
    from loguru import logger  # noqa: F401
    HAS_LOGURU = True
except Exception:
    logger = None
    HAS_LOGURU = False


class DojiAshiStrategyV4(bt.Strategy):
    """
    Doji Ashi Strategy v4 - 多重过滤器交易策略 + Plotly可视化
    基于Pine Script v2.6的完整实现，支持市场类型预设、多重过滤器和高级Plotly图表
    """
    
    params = (
        # === MODE SELECTOR === #
        ("market_type", "Crypto"),  # 'Stocks' | 'Crypto'
        ("trade_direction", "both"),  # 'long' | 'short' | 'both'
        
        # === FILTER CONTROLS === #
        ("enable_market_filter_input", False),  # 手动开启市场过滤器（仅Stocks模式）
        ("enable_relative_strength", False),    # 相对强度过滤器（仅Stocks模式）
        ("enable_daily_trend_filter", True),    # 日线趋势过滤器
        ("trend_mode", "strict"),               # 'strict' | 'flexible'
        ("enable_volume_filter", False),        # 相对成交量过滤器
        ("enable_time_filter", False),          # 时间过滤器
        ("enable_vwap_filter_entry", False),    # VWAP入场过滤器
        ("enable_entry_trigger", True),         # 3/8 MA触发器
        
        # === TRIGGER SETTINGS === #
        ("trigger_ma_type", "EMA"),            # 'EMA' only for now
        ("entry_mode", "above_below"),         # 'cross' | 'above_below'
        ("fast_ma_len", 3),                    # 快速MA长度
        ("slow_ma_len", 8),                    # 慢速MA长度
        
        # === TIME FILTER SETTINGS === #
        ("ignore_hour", 14),                   # UTC小时
        ("ignore_minute", 30),                 # UTC分钟  
        ("ignore_minutes", 30),                # 忽略分钟数
        
        # === DAILY TREND FILTER === #
        ("daily_sma_20", 20),                  # 日线SMA20
        ("daily_sma_50", 50),                  # 日线SMA50
        ("daily_sma_200", 200),                # 日线SMA200
        
        # === VOLUME FILTER === #
        ("volume_ma_len", 20),                 # 成交量MA长度
        ("volume_factor", 1.2),                # 成交量倍数阈值
        
        # === RELATIVE STRENGTH FILTER === #
        ("rs_ma_len", 20),                     # 相对强度MA长度
        
        # === SL/TP SETTINGS === #
        ("atr_length", 14),                    # ATR周期
        ("atr_multiplier", 1.5),               # ATR倍数
        ("risk_reward_ratio", 2.0),            # 风险回报比
        
        # === EXIT SETTINGS === #
        ("use_trailing_stop", False),          # 使用追踪止损
        ("trail_offset_percent", 1.0),         # 追踪止损偏移百分比
        ("use_time_exit", False),              # 使用时间退出
        ("max_bars_in_trade", 100),            # 最大持仓K线数
        
        # === POSITION SIZING === #
        ("order_percent", 0.20),               # 每笔交易股权百分比
        ("min_size", 0.001),                   # 最小仓位
        ("size_step", 0.001),                  # 仓位步长
        ("leverage", 4.0),                     # 杠杆
        
        # === TRADING CADENCE === #
        ("cooldown_bars", 10),                 # 冷却K线数
        
        # === TECHNICAL SETTINGS === #
        ("use_talib", True),                   # 优先使用TA-Lib
        ("warmup_daily", 200),                 # 日线指标预热期
        
        # === PLOTLY VISUALIZATION SETTINGS === #
        ("enable_plotly", True),               # 启用Plotly绘图
        ("use_resampler", True),               # 使用plotly-resampler
        ("plot_indicators", True),             # 绘制技术指标
        ("plot_signals", True),                # 绘制交易信号
        ("plot_volume", True),                 # 绘制成交量
        ("plot_save_path", "plots"),           # 图表保存路径
        ("plot_theme", "plotly_dark"),         # 图表主题
        ("max_plot_points", 5000),             # 最大绘图点数（resampler用）
    )

    def __init__(self):
        # 规范化参数
        self.market_type = str(self.p.market_type).lower()
        self.trade_direction = str(self.p.trade_direction).lower()
        self.trend_mode = str(self.p.trend_mode).lower()
        self.entry_mode = str(self.p.entry_mode).lower()
        
        # 基于市场类型自动配置过滤器
        self._configure_market_filters()
        
        # 数据引用
        self.data_close = self.datas[0].close
        self.data_high = self.datas[0].high
        self.data_low = self.datas[0].low
        self.data_open = self.datas[0].open
        self.data_volume = getattr(self.datas[0], "volume", None)
        
        # 多时间框架数据设置
        self.daily_data = self.datas[1] if len(self.datas) > 1 else self.datas[0]
        self.market_data = self.datas[2] if len(self.datas) > 2 else None
        
        # === 日线趋势过滤器 === #
        self._setup_daily_trend_filter()
        
        # === 3/8 MA触发器 === #
        self._setup_ma_trigger()
        
        # === 可选过滤器 === #
        self._setup_optional_filters()
        
        # === ATR和风险管理 === #
        self._setup_risk_management()
        
        # === 状态变量 === #
        self._init_state_variables()
        
        # === 数据收集初始化 === #
        self._init_data_collection()

    def _configure_market_filters(self):
        """基于市场类型自动配置过滤器"""
        if self.market_type == "crypto":
            self.use_btc_filter = True
            self.use_spy_filter = False
            self.enable_market_filter = True
            self.enable_relative_strength = False
        elif self.market_type == "stocks":
            self.use_btc_filter = False
            self.use_spy_filter = True
            self.enable_market_filter = self.p.enable_market_filter_input
            self.enable_relative_strength = self.p.enable_relative_strength
        else:
            self.use_btc_filter = False
            self.use_spy_filter = False
            self.enable_market_filter = False
            self.enable_relative_strength = False

    def _setup_daily_trend_filter(self):
        """设置日线趋势过滤器"""
        self.daily_sma20 = btind.SMA(self.daily_data.close, period=self.p.daily_sma_20)
        self.daily_sma50 = btind.SMA(self.daily_data.close, period=self.p.daily_sma_50)
        self.daily_sma200 = btind.SMA(self.daily_data.close, period=self.p.daily_sma_200)
        
        self.sma_pass_count = (
            (self.daily_data.close > self.daily_sma20) +
            (self.daily_data.close > self.daily_sma50) +
            (self.daily_data.close > self.daily_sma200)
        )
        
        if self.trend_mode == "strict":
            self.daily_uptrend = self.sma_pass_count == 3
            self.daily_downtrend = self.sma_pass_count == 0
        else:  # flexible
            self.daily_uptrend = self.sma_pass_count >= 2
            self.daily_downtrend = self.sma_pass_count <= 1

    def _setup_ma_trigger(self):
        """设置3/8 MA触发器"""
        try:
            if self.p.use_talib and HAS_TALIB:
                self.ma_fast = bt.talib.EMA(self.data_close, timeperiod=self.p.fast_ma_len)
                self.ma_slow = bt.talib.EMA(self.data_close, timeperiod=self.p.slow_ma_len)
            else:
                raise AttributeError
        except Exception:
            self.ma_fast = btind.EMA(self.data_close, period=self.p.fast_ma_len)
            self.ma_slow = btind.EMA(self.data_close, period=self.p.slow_ma_len)
        
        if self.entry_mode == "cross":
            self.sig_long = btind.CrossUp(self.ma_fast, self.ma_slow)
            self.sig_short = btind.CrossDown(self.ma_fast, self.ma_slow)
        else:  # above_below
            self.sig_long = self.ma_fast > self.ma_slow
            self.sig_short = self.ma_fast < self.ma_slow

    def _setup_optional_filters(self):
        """设置可选过滤器"""
        # VWAP过滤器
        if self.p.enable_vwap_filter_entry:
            try:
                self.vwap = btind.VWAP(self.datas[0])
            except Exception:
                self.vwap = None
        else:
            self.vwap = None
            
        # 成交量过滤器
        if self.p.enable_volume_filter and self.data_volume is not None:
            self.avg_volume = btind.SMA(self.data_volume, period=self.p.volume_ma_len)
            self.high_rel_volume = self.data_volume > (self.avg_volume * self.p.volume_factor)
        else:
            self.avg_volume = None
            self.high_rel_volume = None
            
        # 相对强度过滤器（仅Stocks模式）
        if self.enable_relative_strength and self.market_data is not None:
            self.rel_strength_line = self.data_close / self.market_data.close
            self.rel_strength_ma = btind.SMA(self.rel_strength_line, period=self.p.rs_ma_len)
            self.strong_vs_market = self.rel_strength_line > self.rel_strength_ma
            self.weak_vs_market = self.rel_strength_line < self.rel_strength_ma
        else:
            self.strong_vs_market = None
            self.weak_vs_market = None
            
        # 市场过滤器
        if self.enable_market_filter and self.market_data is not None:
            self.market_ma = btind.SMA(self.market_data.close, period=20)
            self.market_bullish = self.market_data.close > self.market_ma
            self.market_bearish = self.market_data.close < self.market_ma
            self.market_strength = (self.market_data.close - self.market_ma) / self.market_ma * 100
        else:
            self.market_bullish = None
            self.market_bearish = None
            self.market_strength = None

    def _setup_risk_management(self):
        """设置风险管理"""
        try:
            if self.p.use_talib and HAS_TALIB:
                self.atr = bt.talib.ATR(self.data_high, self.data_low, self.data_close, 
                                     timeperiod=self.p.atr_length)
            else:
                raise AttributeError
        except Exception:
            self.atr = btind.ATR(self.datas[0], period=self.p.atr_length)

    def _init_state_variables(self):
        """初始化状态变量"""
        self.parent_order = None
        self.sl_order = None
        self.tp_order = None
        self.trail_order = None
        self.entry_bar_index = None
        
        self.last_long_bar = -10**9
        self.last_short_bar = -10**9
        
        self.warmup_daily = max(int(self.p.warmup_daily), 
                               int(self.p.atr_length),
                               int(self.p.daily_sma_200))

    def _init_data_collection(self):
        """初始化数据收集用于Plotly可视化"""
        if not (self.p.enable_plotly and HAS_PLOTLY):
            return
            
        # 数据收集字典
        self.plot_data = {
            # OHLCV数据
            'datetime': [],
            'open': [],
            'high': [],
            'low': [],
            'close': [],
            'volume': [],
            
            # 技术指标
            'ma_fast': [],
            'ma_slow': [],
            'atr': [],
            'daily_sma20': [],
            'daily_sma50': [],
            'daily_sma200': [],
            
            # 交易信号
            'buy_signals': [],
            'sell_signals': [],
            'buy_prices': [],
            'sell_prices': [],
            
            # 持仓和PnL
            'position': [],
            'portfolio_value': [],
            'trades': [],
        }
        
        # 可选指标
        if self.vwap is not None:
            self.plot_data['vwap'] = []
        if self.avg_volume is not None:
            self.plot_data['avg_volume'] = []
        if self.market_data is not None:
            self.plot_data['market_close'] = []
            self.plot_data['market_ma'] = []

    # === 工具函数 === #
    
    def _confirmed_daily(self, line) -> bool:
        """获取确认的日线数据（避免未来函数）"""
        if len(line) < 2:
            return False
        return bool(line[-1])

    def _is_valid_time(self) -> bool:
        """检查时间过滤器"""
        if not self.p.enable_time_filter:
            return True
        return True  # 简化实现

    def _can_enter_long(self) -> bool:
        """检查多头入场条件"""
        conditions = []
        
        current_bar = len(self)
        can_long_cool = current_bar - self.last_long_bar >= int(self.p.cooldown_bars)
        conditions.append(can_long_cool)
        conditions.append(self.trade_direction in ("long", "both"))
        
        if self.p.enable_daily_trend_filter:
            conditions.append(self._confirmed_daily(self.daily_uptrend))
        if self.p.enable_entry_trigger:
            conditions.append(bool(self.sig_long[0]))
        if self.enable_market_filter and self.market_bullish is not None:
            conditions.append(bool(self.market_bullish[0]))
        if self.enable_relative_strength and self.strong_vs_market is not None:
            conditions.append(bool(self.strong_vs_market[0]))
        if self.p.enable_vwap_filter_entry and self.vwap is not None:
            conditions.append(self.data_close[0] > self.vwap[0])
        if self.p.enable_volume_filter and self.high_rel_volume is not None:
            conditions.append(bool(self.high_rel_volume[0]))
        conditions.append(self._is_valid_time())
        
        return all(conditions)

    def _can_enter_short(self) -> bool:
        """检查空头入场条件"""
        conditions = []
        
        current_bar = len(self)
        can_short_cool = current_bar - self.last_short_bar >= int(self.p.cooldown_bars)
        conditions.append(can_short_cool)
        conditions.append(self.trade_direction in ("short", "both"))
        
        if self.p.enable_daily_trend_filter:
            conditions.append(self._confirmed_daily(self.daily_downtrend))
        if self.p.enable_entry_trigger:
            conditions.append(bool(self.sig_short[0]))
        if self.enable_market_filter and self.market_bearish is not None:
            conditions.append(bool(self.market_bearish[0]))
        if self.enable_relative_strength and self.weak_vs_market is not None:
            conditions.append(bool(self.weak_vs_market[0]))
        if self.p.enable_vwap_filter_entry and self.vwap is not None:
            conditions.append(self.data_close[0] < self.vwap[0])
        if self.p.enable_volume_filter and self.high_rel_volume is not None:
            conditions.append(bool(self.high_rel_volume[0]))
        conditions.append(self._is_valid_time())
        
        return all(conditions)

    def _calc_position_size(self) -> float:
        """计算仓位大小"""
        equity = float(self.broker.getvalue())
        price = float(self.data_close[0])
        
        if equity <= 0 or price <= 0:
            return 0.0
            
        position_value = equity * float(self.p.order_percent) * float(self.p.leverage)
        raw_size = position_value / price
        size = max(self.p.min_size, float(raw_size))
        
        step = float(self.p.size_step or 0.0)
        if step > 0:
            size = (int(size / step)) * step
            
        return size

    def _cleanup_orders(self):
        """清理已完成的订单"""
        for name in ("parent_order", "sl_order", "tp_order", "trail_order"):
            order = getattr(self, name)
            if order is not None and not order.alive():
                setattr(self, name, None)

    def _collect_plot_data(self):
        """收集当前K线的数据用于绘图"""
        if not (self.p.enable_plotly and HAS_PLOTLY):
            return
            
        # 基础OHLCV数据
        self.plot_data['datetime'].append(self.datas[0].datetime.datetime(0))
        self.plot_data['open'].append(float(self.data_open[0]))
        self.plot_data['high'].append(float(self.data_high[0]))
        self.plot_data['low'].append(float(self.data_low[0]))
        self.plot_data['close'].append(float(self.data_close[0]))
        self.plot_data['volume'].append(float(self.data_volume[0]) if self.data_volume else 0)
        
        # 技术指标
        self.plot_data['ma_fast'].append(float(self.ma_fast[0]) if len(self.ma_fast) > 0 else np.nan)
        self.plot_data['ma_slow'].append(float(self.ma_slow[0]) if len(self.ma_slow) > 0 else np.nan)
        self.plot_data['atr'].append(float(self.atr[0]) if len(self.atr) > 0 else np.nan)
        
        # 日线指标（使用当前值）
        self.plot_data['daily_sma20'].append(float(self.daily_sma20[0]) if len(self.daily_sma20) > 0 else np.nan)
        self.plot_data['daily_sma50'].append(float(self.daily_sma50[0]) if len(self.daily_sma50) > 0 else np.nan)
        self.plot_data['daily_sma200'].append(float(self.daily_sma200[0]) if len(self.daily_sma200) > 0 else np.nan)
        
        # 可选指标
        if 'vwap' in self.plot_data:
            self.plot_data['vwap'].append(float(self.vwap[0]) if self.vwap and len(self.vwap) > 0 else np.nan)
        if 'avg_volume' in self.plot_data:
            self.plot_data['avg_volume'].append(float(self.avg_volume[0]) if self.avg_volume and len(self.avg_volume) > 0 else np.nan)
        if 'market_close' in self.plot_data and self.market_data:
            self.plot_data['market_close'].append(float(self.market_data.close[0]))
            self.plot_data['market_ma'].append(float(self.market_ma[0]) if self.market_ma and len(self.market_ma) > 0 else np.nan)
        
        # 交易信号占位符（在实际交易时更新）
        self.plot_data['buy_signals'].append(False)
        self.plot_data['sell_signals'].append(False)
        self.plot_data['buy_prices'].append(np.nan)
        self.plot_data['sell_prices'].append(np.nan)
        
        # 持仓和组合价值
        self.plot_data['position'].append(float(self.position.size if self.position else 0))
        self.plot_data['portfolio_value'].append(float(self.broker.getvalue()))

    def _record_trade_signal(self, signal_type: str, price: float):
        """记录交易信号"""
        if not (self.p.enable_plotly and HAS_PLOTLY):
            return
            
        current_idx = len(self.plot_data['datetime']) - 1
        if current_idx >= 0:
            if signal_type == 'buy':
                self.plot_data['buy_signals'][current_idx] = True
                self.plot_data['buy_prices'][current_idx] = price
            elif signal_type == 'sell':
                self.plot_data['sell_signals'][current_idx] = True
                self.plot_data['sell_prices'][current_idx] = price

    # === 主要回调函数 === #
    
    def next(self):
        """主要逻辑循环"""
        self._cleanup_orders()
        
        # 收集绘图数据
        self._collect_plot_data()
        
        # 预热期检查
        if len(self.daily_data) < self.warmup_daily:
            return
            
        # 如果有未完成订单或持仓，管理退出
        if self.parent_order or self.sl_order or self.tp_order or self.trail_order or self.position:
            self._manage_exits()
            return
            
        # 入场逻辑
        current_bar = len(self)
        
        if self._can_enter_long():
            size = self._calc_position_size()
            if size > 0:
                self.parent_order = self.buy(size=size)
                self.last_long_bar = current_bar
                self._record_trade_signal('buy', float(self.data_close[0]))
                
        elif self._can_enter_short():
            size = self._calc_position_size()
            if size > 0:
                self.parent_order = self.sell(size=size)
                self.last_short_bar = current_bar
                self._record_trade_signal('sell', float(self.data_close[0]))

    def _manage_exits(self):
        """管理退出条件"""
        if not self.position:
            return
            
        if (self.p.use_time_exit and 
            self.entry_bar_index is not None and
            (len(self) - int(self.entry_bar_index)) >= int(self.p.max_bars_in_trade)):
            
            self._close_position("Time Exit")

    def _close_position(self, reason="Manual"):
        """关闭仓位和相关订单"""
        for order in [self.sl_order, self.tp_order, self.trail_order]:
            if order and order.alive():
                self.cancel(order)
                
        self.close()
        self.sl_order = self.tp_order = self.trail_order = None
        self.entry_bar_index = None

    def _create_exit_orders(self, order: bt.Order):
        """创建退出订单"""
        executed_price = float(order.executed.price)
        size = float(order.executed.size)
        atr_value = float(self.atr[0])
        
        if self.p.use_trailing_stop:
            if order.isbuy():
                self.trail_order = self.sell(
                    exectype=bt.Order.StopTrail,
                    trailpercent=self.p.trail_offset_percent / 100.0,
                    size=size
                )
            else:
                self.trail_order = self.buy(
                    exectype=bt.Order.StopTrail,
                    trailpercent=self.p.trail_offset_percent / 100.0,
                    size=size
                )
        else:
            if order.isbuy():
                sl_price = executed_price - atr_value * float(self.p.atr_multiplier)
                tp_price = executed_price + (executed_price - sl_price) * float(self.p.risk_reward_ratio)
                
                tp_order = self.sell(exectype=bt.Order.Limit, price=tp_price, size=size)
                self.sl_order = self.sell(exectype=bt.Order.Stop, price=sl_price, size=size, oco=tp_order)
                self.tp_order = tp_order
            else:
                sl_price = executed_price + atr_value * float(self.p.atr_multiplier)
                tp_price = executed_price - (sl_price - executed_price) * float(self.p.risk_reward_ratio)
                
                tp_order = self.buy(exectype=bt.Order.Limit, price=tp_price, size=size)
                self.sl_order = self.buy(exectype=bt.Order.Stop, price=sl_price, size=size, oco=tp_order)
                self.tp_order = tp_order

    # === 通知回调 === #
    
    def notify_order(self, order):
        """订单状态通知"""
        if order.status in [order.Submitted, order.Accepted]:
            return
            
        if order.status == order.Completed:
            if order == self.parent_order:
                self.entry_bar_index = len(self)
                self._create_exit_orders(order)
                self.parent_order = None
            else:
                if order == self.sl_order:
                    self.sl_order = None
                elif order == self.tp_order:
                    self.tp_order = None
                elif order == self.trail_order:
                    self.trail_order = None
                    
                if not self.position:
                    self.sl_order = self.tp_order = self.trail_order = None
                    self.entry_bar_index = None
                    
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            if order == self.parent_order:
                self.parent_order = None
            elif order == self.sl_order:
                self.sl_order = None
            elif order == self.tp_order:
                self.tp_order = None
            elif order == self.trail_order:
                self.trail_order = None

    def notify_trade(self, trade):
        """交易通知"""
        if trade.isclosed:
            self.sl_order = self.tp_order = self.trail_order = None
            self.entry_bar_index = None
            
            # 记录交易数据用于绘图
            if self.p.enable_plotly and HAS_PLOTLY:
                # 计算退出价格，避免除零错误
                exit_price = trade.price
                if trade.size != 0:
                    exit_price = trade.pnl / trade.size + trade.price
                
                # 计算持仓天数
                duration = 0
                try:
                    if trade.dtclose and trade.dtopen:
                        if hasattr(trade.dtclose - trade.dtopen, 'days'):
                            duration = (trade.dtclose - trade.dtopen).days
                        else:
                            # 如果是浮点数表示的天数
                            duration = int(abs(trade.dtclose - trade.dtopen))
                except Exception:
                    duration = 0
                    
                trade_data = {
                    'entry_date': trade.dtopen,
                    'exit_date': trade.dtclose,
                    'entry_price': trade.price,
                    'exit_price': exit_price,
                    'size': trade.size,
                    'pnl': trade.pnl,
                    'duration': duration,
                }
                self.plot_data['trades'].append(trade_data)

    def create_plotly_chart(self):
        """创建详细的Plotly交互式图表"""
        if not (self.p.enable_plotly and HAS_PLOTLY):
            print("Plotly not available, skipping chart creation")
            return None
            
        if not self.plot_data['datetime']:
            print("No plot data collected")
            return None
            
        # 转换为DataFrame便于操作，确保所有数组长度一致
        min_length = min(len(arr) for arr in self.plot_data.values() if isinstance(arr, list))
        
        # 截断所有数组到相同长度
        trimmed_data = {}
        for key, values in self.plot_data.items():
            if isinstance(values, list) and len(values) > min_length:
                trimmed_data[key] = values[:min_length]
            else:
                trimmed_data[key] = values
                
        df = pd.DataFrame(trimmed_data)
        df.set_index('datetime', inplace=True)
        
        # 使用plotly-resampler处理大数据集
        if HAS_PLOTLY_RESAMPLER and self.p.use_resampler and len(df) > self.p.max_plot_points:
            fig = FigureResampler(make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                subplot_titles=('Price & Indicators', 'Volume', 'Portfolio Value'),
                row_heights=[0.6, 0.2, 0.2]
            ))
        else:
            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                subplot_titles=('Price & Indicators', 'Volume', 'Portfolio Value'),
                row_heights=[0.6, 0.2, 0.2]
            )
        
        # 主图：价格蜡烛图
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='OHLC',
                increasing_line_color='#26a69a',
                decreasing_line_color='#ef5350'
            ),
            row=1, col=1
        )
        
        # 技术指标
        if self.p.plot_indicators:
            # 移动平均线
            fig.add_trace(
                go.Scatter(x=df.index, y=df['ma_fast'], name=f'EMA{self.p.fast_ma_len}',
                          line=dict(color='orange', width=2)),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=df.index, y=df['ma_slow'], name=f'EMA{self.p.slow_ma_len}',
                          line=dict(color='blue', width=2)),
                row=1, col=1
            )
            
            # 日线SMA
            for sma_name, color in [('daily_sma20', 'yellow'), ('daily_sma50', 'purple'), ('daily_sma200', 'red')]:
                if sma_name in df.columns:
                    fig.add_trace(
                        go.Scatter(x=df.index, y=df[sma_name], name=sma_name.upper(),
                                  line=dict(color=color, width=1, dash='dash')),
                        row=1, col=1
                    )
            
            # VWAP（如果启用）
            if 'vwap' in df.columns and self.p.enable_vwap_filter_entry:
                fig.add_trace(
                    go.Scatter(x=df.index, y=df['vwap'], name='VWAP',
                              line=dict(color='brown', width=2)),
                    row=1, col=1
                )
        
        # 交易信号
        if self.p.plot_signals:
            buy_mask = df['buy_signals']
            sell_mask = df['sell_signals']
            
            if buy_mask.any():
                fig.add_trace(
                    go.Scatter(x=df.index[buy_mask], y=df.loc[buy_mask, 'buy_prices'],
                              mode='markers', name='Buy Signals',
                              marker=dict(symbol='triangle-up', size=15, color='green')),
                    row=1, col=1
                )
            
            if sell_mask.any():
                fig.add_trace(
                    go.Scatter(x=df.index[sell_mask], y=df.loc[sell_mask, 'sell_prices'],
                              mode='markers', name='Sell Signals',
                              marker=dict(symbol='triangle-down', size=15, color='red')),
                    row=1, col=1
                )
        
        # 成交量
        if self.p.plot_volume:
            colors = ['green' if close >= open_ else 'red' 
                     for close, open_ in zip(df['close'], df['open'])]
            fig.add_trace(
                go.Bar(x=df.index, y=df['volume'], name='Volume',
                      marker_color=colors, opacity=0.7),
                row=2, col=1
            )
            
            if 'avg_volume' in df.columns and self.p.enable_volume_filter:
                fig.add_trace(
                    go.Scatter(x=df.index, y=df['avg_volume'], name='Avg Volume',
                              line=dict(color='orange', width=1)),
                    row=2, col=1
                )
        
        # 组合价值
        fig.add_trace(
            go.Scatter(x=df.index, y=df['portfolio_value'], name='Portfolio Value',
                      line=dict(color='green', width=2)),
            row=3, col=1
        )
        
        # 更新布局
        fig.update_layout(
            title=f'Doji Ashi Strategy v4 - {self.market_type.upper()} Mode',
            template=self.p.plot_theme,
            height=800,
            showlegend=True,
            xaxis_rangeslider_visible=False
        )
        
        # 更新坐标轴
        fig.update_xaxes(title_text="Date", row=3, col=1)
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        fig.update_yaxes(title_text="Portfolio Value", row=3, col=1)
        
        return fig

    def save_plotly_chart(self, fig=None):
        """保存Plotly图表"""
        if fig is None:
            fig = self.create_plotly_chart()
            
        if fig is None:
            return None
            
        # 创建保存路径
        save_dir = Path(self.p.plot_save_path)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"doji_ashi_v4_{self.market_type}_{timestamp}.html"
        filepath = save_dir / filename
        
        # 保存HTML文件
        fig.write_html(str(filepath))
        
        print(f"Plotly chart saved: {filepath}")
        
        # 尝试自动打开浏览器
        try:
            import webbrowser
            webbrowser.open(f'file://{filepath.absolute()}')
            print("Opening chart in browser...")
        except Exception:
            print(f"Please manually open: {filepath}")
            
        return str(filepath)

    def stop(self):
        """策略结束时的处理"""
        print("\n=== DojiAshiStrategyV4 Parameters ===")
        print(f"Market Type: {self.market_type.upper()}")
        print(f"Trade Direction: {self.trade_direction}")
        print(f"Filters - Daily:{self.p.enable_daily_trend_filter}({self.trend_mode}) "
              f"Market:{self.enable_market_filter} RS:{self.enable_relative_strength}")
        print(f"Filters - Volume:{self.p.enable_volume_filter} VWAP:{self.p.enable_vwap_filter_entry} "
              f"Time:{self.p.enable_time_filter}")
        print(f"MA Trigger: {self.p.enable_entry_trigger} ({self.p.fast_ma_len}/{self.p.slow_ma_len} {self.entry_mode})")
        print(f"Risk Management: ATR({self.p.atr_length}×{self.p.atr_multiplier}) RR:{self.p.risk_reward_ratio}")
        print(f"Position: {self.p.order_percent*100}% equity, {self.p.leverage}× leverage")
        print(f"Exits: Trailing:{self.p.use_trailing_stop}({self.p.trail_offset_percent}%) "
              f"Time:{self.p.use_time_exit}({self.p.max_bars_in_trade}bars)")
        
        # Plotly图表相关信息
        if self.p.enable_plotly and HAS_PLOTLY:
            print(f"Plotly: Enabled (Theme: {self.p.plot_theme}, Resampler: {self.p.use_resampler and HAS_PLOTLY_RESAMPLER})")
            print(f"Data Points Collected: {len(self.plot_data['datetime'])}")
            print(f"Trades Recorded: {len(self.plot_data['trades'])}")
            
            # 创建并保存图表
            try:
                self.save_plotly_chart()
            except Exception as e:
                print(f"Error creating Plotly chart: {e}")
        else:
            print("Plotly: Disabled or not available")
            
        print("=====================================")
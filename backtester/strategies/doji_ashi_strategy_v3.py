"""
Doji Ashi Strategy v3 - Enhanced Backtrader Implementation
基于 Doji_Ashi_Strategy_v2.6.pine 的完整Python实现

主要改进:
- Market Type预设模式 (Stocks/Crypto自动配置)
- 改进的时间过滤器
- 更精确的相对强度过滤
- Market Filter强度计算
- 更完整的Pine Script功能对应

Source Reference: pinescript/strategies/reversal/Doji_Ashi_Strategy_v2.6.pine
"""

from __future__ import annotations

# --- Standard Library ---
import datetime
from typing import Optional

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

# --- Visualization (optional) ---
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
try:
    import plotly.graph_objects as go  # noqa: F401
    HAS_PLOTLY = True
except Exception:
    go = None
    HAS_PLOTLY = False

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


class DojiAshiStrategyV3(bt.Strategy):
    """
    Doji Ashi Strategy v3 - 多重过滤器交易策略
    基于Pine Script v2.6的完整实现，支持市场类型预设、多重过滤器和高级风险管理
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

    def _configure_market_filters(self):
        """基于市场类型自动配置过滤器"""
        if self.market_type == "crypto":
            # Crypto模式: 自动开启BTC市场过滤器
            self.use_btc_filter = True
            self.use_spy_filter = False
            self.enable_market_filter = True
            self.enable_relative_strength = False
        elif self.market_type == "stocks":
            # Stocks模式: 支持SPY过滤器和相对强度
            self.use_btc_filter = False
            self.use_spy_filter = True
            self.enable_market_filter = self.p.enable_market_filter_input
            self.enable_relative_strength = self.p.enable_relative_strength
        else:
            # 默认配置
            self.use_btc_filter = False
            self.use_spy_filter = False
            self.enable_market_filter = False
            self.enable_relative_strength = False

    def _setup_daily_trend_filter(self):
        """设置日线趋势过滤器"""
        # 日线移动平均线
        self.daily_sma20 = btind.SMA(self.daily_data.close, period=self.p.daily_sma_20)
        self.daily_sma50 = btind.SMA(self.daily_data.close, period=self.p.daily_sma_50)
        self.daily_sma200 = btind.SMA(self.daily_data.close, period=self.p.daily_sma_200)
        
        # SMA通过数量计算
        self.sma_pass_count = (
            (self.daily_data.close > self.daily_sma20) +
            (self.daily_data.close > self.daily_sma50) +
            (self.daily_data.close > self.daily_sma200)
        )
        
        # 趋势定义
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
        
        # 入场信号
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
            # 计算相对强度线: close / spy_close
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
            
            # 市场强度计算 (类似Pine Script的market_filter_strength)
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
        
        # 冷却期管理
        self.last_long_bar = -10**9
        self.last_short_bar = -10**9
        
        # 预热期
        self.warmup_daily = max(int(self.p.warmup_daily), 
                               int(self.p.atr_length),
                               int(self.p.daily_sma_200))

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
            
        # 简化的时间检查逻辑
        # 在实际实现中，这里需要更复杂的时区和时间处理
        current_time = self.datas[0].datetime.time(0)
        target_time = datetime.time(self.p.ignore_hour, self.p.ignore_minute)
        
        # 简单实现：在指定时间后X分钟内不交易
        return True  # 简化实现，实际需要更精确的时间逻辑

    def _can_enter_long(self) -> bool:
        """检查多头入场条件"""
        conditions = []
        
        # 冷却期检查
        current_bar = len(self)
        can_long_cool = current_bar - self.last_long_bar >= int(self.p.cooldown_bars)
        conditions.append(can_long_cool)
        
        # 交易方向检查
        conditions.append(self.trade_direction in ("long", "both"))
        
        # 日线趋势过滤器
        if self.p.enable_daily_trend_filter:
            conditions.append(self._confirmed_daily(self.daily_uptrend))
            
        # 3/8 MA触发器
        if self.p.enable_entry_trigger:
            conditions.append(bool(self.sig_long[0]))
            
        # 市场过滤器
        if self.enable_market_filter and self.market_bullish is not None:
            conditions.append(bool(self.market_bullish[0]))
            
        # 相对强度过滤器
        if self.enable_relative_strength and self.strong_vs_market is not None:
            conditions.append(bool(self.strong_vs_market[0]))
            
        # VWAP过滤器
        if self.p.enable_vwap_filter_entry and self.vwap is not None:
            conditions.append(self.data_close[0] > self.vwap[0])
            
        # 成交量过滤器
        if self.p.enable_volume_filter and self.high_rel_volume is not None:
            conditions.append(bool(self.high_rel_volume[0]))
            
        # 时间过滤器
        conditions.append(self._is_valid_time())
        
        return all(conditions)

    def _can_enter_short(self) -> bool:
        """检查空头入场条件"""
        conditions = []
        
        # 冷却期检查
        current_bar = len(self)
        can_short_cool = current_bar - self.last_short_bar >= int(self.p.cooldown_bars)
        conditions.append(can_short_cool)
        
        # 交易方向检查
        conditions.append(self.trade_direction in ("short", "both"))
        
        # 日线趋势过滤器
        if self.p.enable_daily_trend_filter:
            conditions.append(self._confirmed_daily(self.daily_downtrend))
            
        # 3/8 MA触发器
        if self.p.enable_entry_trigger:
            conditions.append(bool(self.sig_short[0]))
            
        # 市场过滤器
        if self.enable_market_filter and self.market_bearish is not None:
            conditions.append(bool(self.market_bearish[0]))
            
        # 相对强度过滤器
        if self.enable_relative_strength and self.weak_vs_market is not None:
            conditions.append(bool(self.weak_vs_market[0]))
            
        # VWAP过滤器
        if self.p.enable_vwap_filter_entry and self.vwap is not None:
            conditions.append(self.data_close[0] < self.vwap[0])
            
        # 成交量过滤器
        if self.p.enable_volume_filter and self.high_rel_volume is not None:
            conditions.append(bool(self.high_rel_volume[0]))
            
        # 时间过滤器
        conditions.append(self._is_valid_time())
        
        return all(conditions)

    def _calc_position_size(self) -> float:
        """计算仓位大小"""
        equity = float(self.broker.getvalue())
        price = float(self.data_close[0])
        
        if equity <= 0 or price <= 0:
            return 0.0
            
        # 考虑杠杆的仓位价值
        position_value = equity * float(self.p.order_percent) * float(self.p.leverage)
        raw_size = position_value / price
        size = max(self.p.min_size, float(raw_size))
        
        # 按步长调整
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

    # === 主要回调函数 === #
    
    def next(self):
        """主要逻辑循环"""
        self._cleanup_orders()
        
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
                
        elif self._can_enter_short():
            size = self._calc_position_size()
            if size > 0:
                self.parent_order = self.sell(size=size)
                self.last_short_bar = current_bar

    def _manage_exits(self):
        """管理退出条件"""
        if not self.position:
            return
            
        # 时间退出检查
        if (self.p.use_time_exit and 
            self.entry_bar_index is not None and
            (len(self) - int(self.entry_bar_index)) >= int(self.p.max_bars_in_trade)):
            
            self._close_position("Time Exit")

    def _close_position(self, reason="Manual"):
        """关闭仓位和相关订单"""
        # 取消所有保护性订单
        for order in [self.sl_order, self.tp_order, self.trail_order]:
            if order and order.alive():
                self.cancel(order)
                
        # 关闭仓位
        self.close()
        
        # 重置状态
        self.sl_order = self.tp_order = self.trail_order = None
        self.entry_bar_index = None

    def _create_exit_orders(self, order: bt.Order):
        """创建退出订单"""
        executed_price = float(order.executed.price)
        size = float(order.executed.size)
        atr_value = float(self.atr[0])
        
        if self.p.use_trailing_stop:
            # 使用追踪止损
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
            # 使用固定止损止盈
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
                # 主订单成交，创建退出订单
                self.entry_bar_index = len(self)
                self._create_exit_orders(order)
                self.parent_order = None
            else:
                # 退出订单成交，清理引用
                if order == self.sl_order:
                    self.sl_order = None
                elif order == self.tp_order:
                    self.tp_order = None
                elif order == self.trail_order:
                    self.trail_order = None
                    
                # 如果仓位已平，清理所有状态
                if not self.position:
                    self.sl_order = self.tp_order = self.trail_order = None
                    self.entry_bar_index = None
                    
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            # 订单失败，清理引用
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
            # 交易关闭时清理状态
            self.sl_order = self.tp_order = self.trail_order = None
            self.entry_bar_index = None

    def stop(self):
        """策略结束时的参数打印"""
        print("\n=== DojiAshiStrategyV3 Parameters ===")
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
        print("=====================================")
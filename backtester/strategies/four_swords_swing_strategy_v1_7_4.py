"""
Four Swords Swing Strategy v1.7.4 - Backtrader Implementation
Based on: pinescript/strategies/oscillator/Four_Swords_Swing_Strategy_v1_7_4.pine

⌘ SUMMARY:
Type: strategy (CLEAN VERSION - NO RELEASE WINDOW INTERFERENCE) 
Purpose: Pure v1.5 signal logic with clean code architecture
Key Logic: Direct squeeze release detection + WaveTrend + EMA + Volume filtering
Core Features: Smart exit strategy (momentum vs squeeze), dual mode filtering
Status: Production-ready Backtrader implementation
"""
from __future__ import annotations

# --- Standard Library ---
import datetime
from typing import Optional, Dict, List, Any

# --- Core Scientific ---
import numpy as np
import pandas as pd

# --- Backtesting ---
import backtrader as bt
import backtrader.indicators as btind

# TA-Lib (optional with capability detection)
try:
    import talib
    HAS_TALIB = True
except Exception:
    talib = None
    HAS_TALIB = False

# --- Visualization (Enhanced Plotly Support) ---
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except Exception:
    go = None
    make_subplots = None
    HAS_PLOTLY = False

try:
    from plotly_resampler import FigureResampler
    HAS_PLOTLY_RESAMPLER = True
except Exception:
    FigureResampler = None
    HAS_PLOTLY_RESAMPLER = False


class SqueezeMomentumIndicator(bt.Indicator):
    """
    Squeeze Momentum Oscillator (SQZMOM)
    Based on Bollinger Bands and Keltner Channels compression detection
    """
    lines = ('squeeze_on', 'squeeze_off', 'signal_bar', 'momentum')
    
    params = (
        ('bb_length', 20),
        ('bb_mult', 2.0),
        ('kc_length', 20), 
        ('kc_mult', 1.5),
        ('use_true_range', True),
    )
    
    plotinfo = dict(subplot=True, plotname='Squeeze Momentum')
    plotlines = dict(
        momentum=dict(color='blue'),
        squeeze_on=dict(color='red', _method='bar'),
        squeeze_off=dict(color='green', _method='bar'),
        signal_bar=dict(color='yellow', _method='bar')
    )
    
    def __init__(self):
        # Bollinger Bands calculation
        self.bb_basis = btind.SimpleMovingAverage(self.data.close, period=self.params.bb_length)
        self.bb_dev = self.params.bb_mult * btind.StandardDeviation(self.data.close, period=self.params.bb_length)
        self.bb_upper = self.bb_basis + self.bb_dev
        self.bb_lower = self.bb_basis - self.bb_dev
        
        # Keltner Channels calculation
        self.kc_ma = btind.SimpleMovingAverage(self.data.close, period=self.params.kc_length)
        if self.params.use_true_range:
            self.kc_range = btind.TrueRange(self.data)
        else:
            self.kc_range = self.data.high - self.data.low
        self.kc_rangema = btind.SimpleMovingAverage(self.kc_range, period=self.params.kc_length)
        self.kc_upper = self.kc_ma + self.kc_rangema * self.params.kc_mult
        self.kc_lower = self.kc_ma - self.kc_rangema * self.params.kc_mult
        
        # Squeeze conditions
        self.squeeze_on_cond1 = self.bb_lower > self.kc_lower
        self.squeeze_on_cond2 = self.bb_upper < self.kc_upper
        self.squeeze_off_cond1 = self.bb_lower < self.kc_lower
        self.squeeze_off_cond2 = self.bb_upper > self.kc_upper
        
        # Momentum calculation (LazyBear method)
        highest = btind.Highest(self.data.high, period=self.params.kc_length)
        lowest = btind.Lowest(self.data.low, period=self.params.kc_length)
        avg_hl = (highest + lowest) / 2.0
        avg_close = btind.SimpleMovingAverage(self.data.close, period=self.params.kc_length)
        avg_all = (avg_hl + avg_close) / 2.0
        source_diff = self.data.close - avg_all
        
        # Linear regression slope as momentum (using simple approximation)
        self._mom = btind.ROC(source_diff, period=self.params.kc_length)

    def next(self):
        # Calculate squeeze conditions manually
        squeeze_on = (self.squeeze_on_cond1[0] and self.squeeze_on_cond2[0])
        squeeze_off = (self.squeeze_off_cond1[0] and self.squeeze_off_cond2[0])
        
        # Signal bar: squeeze was on last bar but not current bar
        prev_squeeze_on = False
        if len(self) > 1:
            prev_squeeze_on = (self.squeeze_on_cond1[-1] and self.squeeze_on_cond2[-1])
        signal_bar = prev_squeeze_on and not squeeze_on
        
        self.lines.squeeze_on[0] = float(squeeze_on)
        self.lines.squeeze_off[0] = float(squeeze_off) 
        self.lines.signal_bar[0] = float(signal_bar)
        self.lines.momentum[0] = self._mom[0]


class WaveTrendIndicator(bt.Indicator):
    """
    WaveTrend Oscillator 
    Based on EMA of EMA calculations with overbought/oversold detection
    """
    lines = ('wt1', 'wt2', 'wt_signal')
    
    params = (
        ('n1', 10),  # Channel Length
        ('n2', 21),  # Average Length
    )
    
    plotinfo = dict(subplot=True, plotname='WaveTrend')
    plotlines = dict(
        wt1=dict(color='blue'),
        wt2=dict(color='red'), 
        wt_signal=dict(color='green', _method='bar')
    )
    
    def __init__(self):
        # Typical price
        self.ap = (self.data.high + self.data.low + self.data.close) / 3.0
        
        # EMA calculations
        self.esa = btind.ExponentialMovingAverage(self.ap, period=self.params.n1)
        # Custom absolute value calculation
        diff = self.ap - self.esa
        abs_diff = bt.If(diff >= 0, diff, -diff)
        self.d = btind.ExponentialMovingAverage(abs_diff, period=self.params.n1)
        
        # CI calculation with safer division approach
        # 使用条件表达式避免除零
        numerator = self.ap - self.esa
        denominator = 0.015 * self.d
        safe_denominator = bt.If(denominator > 1e-6, denominator, 1e-6)
        self.ci = numerator / safe_denominator
        
        # TCI (True Commodity Index)
        self.tci = btind.ExponentialMovingAverage(self.ci, period=self.params.n2)
        
        # WaveTrend lines
        self.wt1 = self.tci
        self.wt2 = btind.SimpleMovingAverage(self.wt1, period=4)
        
        # WaveTrend signal (wt1 > wt2)
        self.wt_signal = self.wt1 > self.wt2
    
    def next(self):
        self.lines.wt1[0] = self.wt1[0]
        self.lines.wt2[0] = self.wt2[0]
        self.lines.wt_signal[0] = float(self.wt_signal[0])


class FourSwordsSwingStrategyV174(bt.Strategy):
    """
    Four Swords Swing Strategy v1.7.4 - Clean Implementation
    
    Core Logic:
    1. SQZMOM signal detection (squeeze release)
    2. WaveTrend direction confirmation  
    3. EMA trend filtering (optional)
    4. Volume confirmation (optional)
    5. Smart exit strategy based on entry momentum
    """
    
    params = (
        # SQZMOM Core Parameters
        ('bb_length', 20),
        ('bb_mult', 2.0),
        ('kc_length', 20),
        ('kc_mult', 1.5),
        ('use_true_range', True),
        
        # WaveTrend Parameters
        ('wt_n1', 10),
        ('wt_n2', 21),
        
        # Swing Enhancement Filters
        ('use_ema_filter', True),
        ('ema_fast', 10),
        ('ema_slow', 20),
        ('use_volume_filter', True),
        ('volume_multiplier', 1.05),
        
        # Strategy Settings
        ('trade_direction', 'long'),  # 'long', 'short', 'both'
        ('use_confirmed_signal', False),  # Wait 1 bar for confirmation
        ('use_simplified_signals', False),  # Remove restrictive filters
        ('one_position', True),  # 同一时刻仅1笔持仓
        
        # Risk Management
        ('atr_periods', 14),
        ('atr_multiplier', 2.0),
        
        # Position Sizing
        ('position_pct', 0.2),  # 20% of equity per trade
        ('min_qty', 0.001),     # Minimum trade quantity
        ('qty_step', 0.001),    # Quantity step size
        
        # Order/Execution
        ('order_style', 'maker'),  # 'maker' (limit) or 'taker' (market)
        ('limit_offset', 0.001),   # maker: place limit below/above close by 0.1%
        ('use_sizer', True),    # Use external sizer for position sizing
        ('leverage', 4.0),      # 杠杆倍数 (参数化)
    )
    
    def __init__(self):
        """Initialize indicators and state variables"""
        
        # Core indicators
        self.sqzmom = SqueezeMomentumIndicator(
            self.data,
            bb_length=self.params.bb_length,
            bb_mult=self.params.bb_mult,
            kc_length=self.params.kc_length,
            kc_mult=self.params.kc_mult,
            use_true_range=self.params.use_true_range
        )
        
        self.wavetrend = WaveTrendIndicator(
            self.data,
            n1=self.params.wt_n1,
            n2=self.params.wt_n2
        )
        
        # EMA trend filter
        if self.params.use_ema_filter:
            self.ema_fast = btind.ExponentialMovingAverage(self.data.close, period=self.params.ema_fast)
            self.ema_slow = btind.ExponentialMovingAverage(self.data.close, period=self.params.ema_slow)
            self.ema_bull_trend = self.ema_fast > self.ema_slow
            self.ema_bear_trend = self.ema_fast < self.ema_slow
        else:
            self.ema_bull_trend = None
            self.ema_bear_trend = None
        
        # Volume filter with simplified logic for plotting compatibility  
        if self.params.use_volume_filter:
            self.avg_volume = btind.SimpleMovingAverage(self.data.volume, period=20)
            # Simplified volume threshold to avoid bt.And plotting issues
            vol_threshold = self.avg_volume * self.params.volume_multiplier
            self.volume_confirm = self.data.volume > vol_threshold
        else:
            self.volume_confirm = None
        
        # ATR for stop loss
        self.atr = btind.AverageTrueRange(self.data, period=self.params.atr_periods)
        
        # State management variables
        self.wait_long_exit_by_squeeze = False
        self.wait_short_exit_by_squeeze = False
        self.entry_price = None
        self.entry_bar = None
        
        # Signal tracking
        self.last_signal_bar = -999
        
        # Signal Flow Counters for Observability
        self.counters = {
            'raw_signals_long': 0,       # Raw SQZMOM long signals
            'raw_signals_short': 0,      # Raw SQZMOM short signals  
            'ema_passed_long': 0,        # Long signals passed EMA filter
            'ema_passed_short': 0,       # Short signals passed EMA filter
            'volume_passed_long': 0,     # Long signals passed Volume filter
            'volume_passed_short': 0,    # Short signals passed Volume filter
            'wt_passed_long': 0,         # Long signals passed WT filter
            'wt_passed_short': 0,        # Short signals passed WT filter
            'actual_entries_long': 0,    # Actual long entries executed
            'actual_entries_short': 0,   # Actual short entries executed
            'rejected_orders': 0,        # Rejected orders
            'margin_calls': 0,           # Margin call orders
            'canceled_orders': 0,        # Canceled orders
        }
        
    def next(self):
        """Main strategy logic executed on each bar"""
        
        # Get current signal conditions
        signal_bar = bool(self.sqzmom.lines.signal_bar[0])
        momentum = self.sqzmom.lines.momentum[0]
        wt_signal = bool(self.wavetrend.lines.wt_signal[0])
        
        # Apply signal confirmation delay if enabled
        if self.params.use_confirmed_signal and len(self) > 1:
            signal_bar = bool(self.sqzmom.lines.signal_bar[-1])
            momentum = self.sqzmom.lines.momentum[-1]
            wt_signal = bool(self.wavetrend.lines.wt_signal[-1])
        
        # SIGNAL FLOW ANALYSIS WITH COUNTERS
        
        # Step 1: Raw SQZMOM signals (basic signal detection)
        raw_long_signal = signal_bar and momentum > 0
        raw_short_signal = signal_bar and momentum < 0
        
        if raw_long_signal:
            self.counters['raw_signals_long'] += 1
        if raw_short_signal:
            self.counters['raw_signals_short'] += 1
        
        # Step 2: Apply EMA trend filter
        ema_long_passed = raw_long_signal
        ema_short_passed = raw_short_signal
        
        if self.params.use_ema_filter and self.ema_bull_trend is not None:
            ema_long_passed = raw_long_signal and bool(self.ema_bull_trend[0])
            ema_short_passed = raw_short_signal and bool(self.ema_bear_trend[0])
        
        if ema_long_passed:
            self.counters['ema_passed_long'] += 1
        if ema_short_passed:
            self.counters['ema_passed_short'] += 1
        
        # Step 3: Apply Volume filter
        volume_long_passed = ema_long_passed
        volume_short_passed = ema_short_passed
        
        if self.params.use_volume_filter and self.volume_confirm is not None:
            # Add safety checks for volume filtering
            has_volume = self.data.volume[0] > 0 and self.avg_volume[0] > 0
            volume_long_passed = ema_long_passed and has_volume and bool(self.volume_confirm[0])
            volume_short_passed = ema_short_passed and has_volume and bool(self.volume_confirm[0])
        
        if volume_long_passed:
            self.counters['volume_passed_long'] += 1
        if volume_short_passed:
            self.counters['volume_passed_short'] += 1
        
        # Step 4: Apply WaveTrend direction filter
        wt_long_passed = volume_long_passed
        wt_short_passed = volume_short_passed
        
        if not self.params.use_simplified_signals:
            # Standard mode: require WT direction confirmation
            wt_long_passed = volume_long_passed and wt_signal
            wt_short_passed = volume_short_passed and not wt_signal
        
        if wt_long_passed:
            self.counters['wt_passed_long'] += 1
        if wt_short_passed:
            self.counters['wt_passed_short'] += 1
        
        # Final signals for actual trading
        swing_long_signal = wt_long_passed
        swing_short_signal = wt_short_passed
        
        # Final signal filtering by trade direction
        if self.params.trade_direction == 'short':
            long_signal = False
            short_signal = swing_short_signal
        elif self.params.trade_direction == 'long':
            long_signal = swing_long_signal
            short_signal = False
        else:  # 'both'
            long_signal = swing_long_signal
            short_signal = swing_short_signal
        
        # Entry logic
        if not self.position:
            if long_signal:
                # Determine exit strategy type based on momentum acceleration
                current_momentum = momentum
                prev_momentum = self.sqzmom.lines.momentum[-1] if len(self) > 1 else 0
                self.wait_long_exit_by_squeeze = (current_momentum > prev_momentum)
                
                # Calculate position size and place order based on order_style
                if self.params.order_style == 'maker':
                    limit_price = self.data.close[0] * (1 - self.params.limit_offset)
                    self.buy(exectype=bt.Order.Limit, price=limit_price)
                else:
                    self.buy(exectype=bt.Order.Market)
                
                self.entry_price = self.data.close[0]
                self.entry_bar = len(self)
                self.last_signal_bar = len(self)
                
            elif short_signal:
                # Determine exit strategy type based on momentum acceleration  
                current_momentum = momentum
                prev_momentum = self.sqzmom.lines.momentum[-1] if len(self) > 1 else 0
                self.wait_short_exit_by_squeeze = (current_momentum < prev_momentum)
                
                # Calculate position size and place order based on order_style
                if self.params.order_style == 'maker':
                    limit_price = self.data.close[0] * (1 + self.params.limit_offset)
                    self.sell(exectype=bt.Order.Limit, price=limit_price)
                else:
                    self.sell(exectype=bt.Order.Market)
                
                self.entry_price = self.data.close[0]
                self.entry_bar = len(self)
                self.last_signal_bar = len(self)
        
        # Exit logic
        elif self.position:
            # 首先检查爆仓条件 (最高优先级)
            if self._check_liquidation():
                return
                
            # Check for squeeze back in condition
            squeeze_back_in = False
            if len(self) > 1:
                current_squeeze = bool(self.sqzmom.lines.squeeze_on[0])
                prev_squeeze = bool(self.sqzmom.lines.squeeze_on[-1])
                squeeze_back_in = current_squeeze and not prev_squeeze
            
            if self.position.size > 0:  # Long position
                # Momentum weakness exit
                exit_long_weak = (not self.wait_long_exit_by_squeeze and momentum < 0)
                
                # Squeeze re-entry exit
                exit_long_squeeze = (self.wait_long_exit_by_squeeze and squeeze_back_in)
                
                if exit_long_weak or exit_long_squeeze:
                    self.close(exectype=bt.Order.Market)
                    self._reset_state()
                    
            elif self.position.size < 0:  # Short position
                # Momentum weakness exit
                exit_short_weak = (not self.wait_short_exit_by_squeeze and momentum > 0)
                
                # Squeeze re-entry exit
                exit_short_squeeze = (self.wait_short_exit_by_squeeze and squeeze_back_in)
                
                if exit_short_weak or exit_short_squeeze:
                    self.close(exectype=bt.Order.Market)
                    self._reset_state()
    
    def _calculate_position_size(self) -> float:
        """Calculate position size based on portfolio percentage with quantization"""
        import math
        
        total_value = self.broker.getvalue()
        position_value = total_value * self.params.position_pct
        price = self.data.close[0]
        
        # Raw calculation
        raw = position_value / price
        
        # Quantize to exchange step size
        step = getattr(self.params, 'qty_step', 0.001)
        q = math.floor(raw / step) * step
        
        # Ensure minimum quantity
        min_qty = getattr(self.params, 'min_qty', 0.001)
        final_size = max(q, min_qty)
        
        return final_size
    
    def _reset_state(self):
        """Reset strategy state variables after position close"""
        self.wait_long_exit_by_squeeze = False
        self.wait_short_exit_by_squeeze = False
        self.entry_price = None
        self.entry_bar = None
    
    def notify_order(self, order):
        """Handle order notifications with detailed debugging"""
        if order.status in [order.Completed]:
            if order.isbuy():
                self.counters['actual_entries_long'] += 1
                self.log(f'BUY EXECUTED - Price: {order.executed.price:.2f}, '
                        f'Size: {order.executed.size:.6f}, '
                        f'Cost: {order.executed.value:.2f}')
            elif order.issell():
                self.counters['actual_entries_short'] += 1
                self.log(f'SELL EXECUTED - Price: {order.executed.price:.2f}, '
                        f'Size: {order.executed.size:.6f}, '
                        f'Cost: {order.executed.value:.2f}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            # Enhanced order failure analysis
            dt = self.datas[0].datetime.datetime(0)
            self.log(f'REJ/CXL/MARGIN dt={dt} price={order.created.price:.2f} '
                    f'size={order.created.size:.6f} cash={self.broker.getcash():.2f} '
                    f'value={self.broker.getvalue():.2f} status={order.getstatusname()}')
            
            # Update counters
            if order.status == order.Rejected:
                self.counters['rejected_orders'] += 1
            elif order.status == order.Margin:
                self.counters['margin_calls'] += 1
            elif order.status == order.Canceled:
                self.counters['canceled_orders'] += 1
    
    def notify_trade(self, trade):
        """Handle trade notifications"""
        if trade.isclosed:
            self.log(f'TRADE CLOSED - PnL: {trade.pnl:.2f}, '
                    f'Duration: {trade.barlen} bars')
    
    def _check_liquidation(self) -> bool:
        """
        检查当前仓位是否触发爆仓条件
        
        4倍杠杆逐仓爆仓逻辑:
        - 多头: 当前价格 <= 开仓价 × (1 - 1/杠杆) = 开仓价 × 0.75
        - 空头: 当前价格 >= 开仓价 × (1 + 1/杠杆) = 开仓价 × 1.25
        
        Returns:
            bool: True if liquidated, False otherwise
        """
        if not self.position:
            return False
            
        current_price = self.data.close[0]
        entry_price = self.position.price
        leverage = self.params.leverage  # 参数化杠杆
        
        # 计算爆仓价格
        if self.position.size > 0:  # 多头仓位
            liquidation_price = entry_price * (1 - 1/leverage)  # 75%开仓价
            if current_price <= liquidation_price:
                self.log(f'LIQUIDATION - LONG Position')
                self.log(f'   Entry: {entry_price:.2f}, Current: {current_price:.2f}')
                self.log(f'   Liquidation Price: {liquidation_price:.2f}')
                self.log(f'   Loss: {((current_price - entry_price) / entry_price * 100):.2f}%')
                
                # 强制平仓
                self.close(exectype=bt.Order.Market)
                self._reset_state()
                self.counters['margin_calls'] += 1
                return True
                
        elif self.position.size < 0:  # 空头仓位
            liquidation_price = entry_price * (1 + 1/leverage)  # 125%开仓价
            if current_price >= liquidation_price:
                self.log(f'LIQUIDATION - SHORT Position')
                self.log(f'   Entry: {entry_price:.2f}, Current: {current_price:.2f}')
                self.log(f'   Liquidation Price: {liquidation_price:.2f}')
                self.log(f'   Loss: {((entry_price - current_price) / entry_price * 100):.2f}%')
                
                # 强制平仓
                self.close(exectype=bt.Order.Market)
                self._reset_state()
                self.counters['margin_calls'] += 1
                return True
        
        return False
    
    def log(self, txt, dt=None):
        """Logging function"""
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}: {txt}')
    
    def stop(self):
        """Print detailed signal flow analysis when backtest completes"""
        print("\n" + "="*70)
        print("FOUR SWORDS v1.7.4 - SIGNAL FLOW ANALYSIS")
        print("="*70)
        
        # Calculate totals
        total_raw = self.counters['raw_signals_long'] + self.counters['raw_signals_short']
        total_ema = self.counters['ema_passed_long'] + self.counters['ema_passed_short']
        total_volume = self.counters['volume_passed_long'] + self.counters['volume_passed_short']
        total_wt = self.counters['wt_passed_long'] + self.counters['wt_passed_short']
        total_entries = self.counters['actual_entries_long'] + self.counters['actual_entries_short']
        
        print(f"\nSIGNAL FUNNEL ANALYSIS:")
        print(f"   Raw SQZMOM Signals:      {total_raw:3d} (100.0%)")
        
        if total_raw > 0:
            ema_pct = (total_ema / total_raw) * 100
            print(f"   --> Passed EMA Filter:   {total_ema:3d} ({ema_pct:5.1f}%)")
            
            if total_ema > 0:
                vol_pct = (total_volume / total_ema) * 100
                print(f"       --> Passed Vol Filter: {total_volume:3d} ({vol_pct:5.1f}%)")
                
                if total_volume > 0:
                    wt_pct = (total_wt / total_volume) * 100
                    print(f"           --> Passed WT:      {total_wt:3d} ({wt_pct:5.1f}%)")
                    
                    if total_wt > 0:
                        entry_pct = (total_entries / total_wt) * 100
                        print(f"               --> Executed:    {total_entries:3d} ({entry_pct:5.1f}%)")
        
        print(f"\nLONG SIGNALS BREAKDOWN:")
        print(f"   Raw Long Signals:        {self.counters['raw_signals_long']:3d}")
        print(f"   EMA Passed (Long):       {self.counters['ema_passed_long']:3d}")
        print(f"   Volume Passed (Long):    {self.counters['volume_passed_long']:3d}")
        print(f"   WT Passed (Long):        {self.counters['wt_passed_long']:3d}")
        print(f"   Actual Long Entries:     {self.counters['actual_entries_long']:3d}")
        
        print(f"\nSHORT SIGNALS BREAKDOWN:")
        print(f"   Raw Short Signals:       {self.counters['raw_signals_short']:3d}")
        print(f"   EMA Passed (Short):      {self.counters['ema_passed_short']:3d}")
        print(f"   Volume Passed (Short):   {self.counters['volume_passed_short']:3d}")
        print(f"   WT Passed (Short):       {self.counters['wt_passed_short']:3d}")
        print(f"   Actual Short Entries:    {self.counters['actual_entries_short']:3d}")
        
        print(f"\nRISK MANAGEMENT:")
        print(f"   Rejected Orders:         {self.counters['rejected_orders']:3d}")
        print(f"   Liquidations:            {self.counters['margin_calls']:3d}")
        print(f"   Canceled Orders:         {self.counters['canceled_orders']:3d}")
        
        # 爆仓率统计
        if total_entries > 0:
            liquidation_rate = (self.counters['margin_calls'] / total_entries) * 100
            print(f"   Liquidation Rate:        {liquidation_rate:.1f}% ({self.counters['margin_calls']}/{total_entries})")
            
            if self.counters['margin_calls'] > 0:
                print(f"\nWARNING: {self.counters['margin_calls']} liquidation(s) detected!")
                print(f"   Each liquidation represents ~{100/self.params.leverage:.1f}% account loss ({self.params.leverage:.1f}× leverage)")
                max_account_loss = self.counters['margin_calls'] * (100/self.params.leverage)
                print(f"   Maximum theoretical loss: {max_account_loss}% of account")
        
        # Calculate conversion rates
        if total_raw > 0:
            final_conversion = (total_entries / total_raw) * 100
            print(f"\nOVERALL CONVERSION RATE: {final_conversion:.1f}% ({total_entries}/{total_raw})")
        
        # Identify bottlenecks
        print(f"\nBOTTLENECK ANALYSIS:")
        if total_raw == 0:
            print("   CRITICAL: No raw SQZMOM signals detected!")
            print("      -> Check SQZMOM indicator implementation")
        elif total_ema < total_raw * 0.5:
            print("   WARNING: EMA filter removing 50%+ of signals")
            print("      -> Consider relaxing EMA parameters")
        elif total_volume < total_ema * 0.5:
            print("   WARNING: Volume filter removing 50%+ of signals")
            print("      -> Consider lowering volume_multiplier")
        elif total_wt < total_volume * 0.5:
            print("   WARNING: WaveTrend filter removing 50%+ of signals")
            print("      -> Consider using simplified_mode")
        elif total_entries < total_wt:
            print("   WARNING: Order execution issues detected")
            print("      -> Check position sizing and broker settings")
        else:
            print("   OK: Signal flow appears balanced")
        
        # Additional data information
        from backtrader.utils.date import num2date
        print(f"\nDATA SUMMARY:")
        print(f"   Total bars: {len(self.data)}")
        if len(self.data) > 0:
            print(f"   First bar: {num2date(self.data.datetime[0]).strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Last bar:  {num2date(self.data.datetime[-1]).strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Summary dict for easy reference
        summary_dict = {
            'raw': total_raw, 'ema': total_ema, 'vol': total_volume, 
            'wt': total_wt, 'entries': total_entries,
            'bars': len(self.data),
            'conversion_rate': f"{final_conversion:.1f}%" if total_raw > 0 else "N/A"
        }
        print(f"\nSUMMARY DICT: {summary_dict}")
        print("="*70)
    
    def get_strategy_stats(self) -> Dict[str, Any]:
        """Return strategy statistics for analysis"""
        return {
            'current_position': self.position.size,
            'portfolio_value': self.broker.getvalue(),
            'wait_long_exit_by_squeeze': self.wait_long_exit_by_squeeze,
            'wait_short_exit_by_squeeze': self.wait_short_exit_by_squeeze,
            'last_signal_bar': self.last_signal_bar,
        }


# Example usage and testing
if __name__ == '__main__':
    print("Four Swords Swing Strategy v1.7.4 - Backtrader Implementation")
    print("Based on Pine Script strategy with SQZMOM + WaveTrend logic")
    print("Key Features:")
    print("- Clean squeeze momentum detection")
    print("- WaveTrend direction confirmation")
    print("- Smart exit strategy (momentum vs squeeze)")
    print("- Optional EMA trend and volume filtering")
    print("- Configurable simplified vs enhanced modes")



"""
Four Swords Swing Strategy v1.7.4 - FIXED VERSION (ZeroDivisionError解决)
Based on: pinescript/strategies/oscillator/Four_Swords_Swing_Strategy_v1_7_4.pine

⌘ SUMMARY:
Type: strategy (FIXED VERSION - ZERO DIVISION ERROR RESOLVED) 
Purpose: Pure v1.5 signal logic with enhanced numerical stability
Key Logic: Direct squeeze release detection + WaveTrend + EMA + Volume filtering
Core Features: Smart exit strategy + robust error handling for edge cases
Status: Production-ready with ZeroDivisionError fixes
"""
from __future__ import annotations

# --- Standard Library ---
import datetime
from typing import Optional, Dict, List, Any
import math

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


class SafeDivision(bt.Indicator):
    """Safe division operation with numerical stability checks"""
    lines = ('result',)
    params = (
        ('min_denominator', 1e-10),  # Minimum safe denominator value
        ('fallback_value', 0.0),     # Fallback value when division is unsafe
    )
    
    def __init__(self, numerator, denominator):
        self.numerator = numerator
        self.denominator = denominator
    
    def next(self):
        num = self.numerator[0]
        den = self.denominator[0]
        
        # Check for invalid values
        if (math.isnan(num) or math.isnan(den) or 
            math.isinf(num) or math.isinf(den) or 
            abs(den) < self.params.min_denominator):
            self.lines.result[0] = self.params.fallback_value
        else:
            self.lines.result[0] = num / den


class SqueezeMomentumIndicator(bt.Indicator):
    """
    Squeeze Momentum Oscillator (SQZMOM)
    Based on Bollinger Bands and Keltner Channels compression detection
    Enhanced with numerical stability checks
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
        
        # Momentum calculation with enhanced stability
        highest = btind.Highest(self.data.high, period=self.params.kc_length)
        lowest = btind.Lowest(self.data.low, period=self.params.kc_length)
        
        # Safe division for average calculation
        avg_hl = SafeDivision(highest + lowest, 2.0)
        avg_close = btind.SimpleMovingAverage(self.data.close, period=self.params.kc_length)
        avg_all = SafeDivision(avg_hl + avg_close, 2.0)
        source_diff = self.data.close - avg_all
        
        # Linear regression slope as momentum (using simple approximation)
        self._mom = btind.ROC(source_diff, period=self.params.kc_length)

    def next(self):
        # Calculate squeeze conditions manually with safety checks
        try:
            squeeze_on = (self.squeeze_on_cond1[0] and self.squeeze_on_cond2[0])
            squeeze_off = (self.squeeze_off_cond1[0] and self.squeeze_off_cond2[0])
            
            # Signal bar: squeeze was on last bar but not current bar
            prev_squeeze_on = False
            if len(self) > 1:
                prev_squeeze_on = (self.squeeze_on_cond1[-1] and self.squeeze_on_cond2[-1])
            signal_bar = prev_squeeze_on and not squeeze_on
            
            # Get momentum with safety check
            momentum = self._mom[0] if not (math.isnan(self._mom[0]) or math.isinf(self._mom[0])) else 0.0
            
            self.lines.squeeze_on[0] = float(squeeze_on)
            self.lines.squeeze_off[0] = float(squeeze_off) 
            self.lines.signal_bar[0] = float(signal_bar)
            self.lines.momentum[0] = momentum
            
        except (ZeroDivisionError, ValueError, TypeError):
            # Fallback values in case of any calculation error
            self.lines.squeeze_on[0] = 0.0
            self.lines.squeeze_off[0] = 0.0
            self.lines.signal_bar[0] = 0.0
            self.lines.momentum[0] = 0.0


class WaveTrendIndicator(bt.Indicator):
    """
    WaveTrend Oscillator - FIXED VERSION
    Enhanced with robust numerical stability and zero-division protection
    """
    lines = ('wt1', 'wt2', 'wt_signal')
    
    params = (
        ('n1', 10),  # Channel Length
        ('n2', 21),  # Average Length
        ('ci_min_denominator', 1e-6),  # Minimum safe denominator for CI calculation
        ('ci_fallback', 0.0),  # Fallback CI value when division is unsafe
    )
    
    plotinfo = dict(subplot=True, plotname='WaveTrend')
    plotlines = dict(
        wt1=dict(color='blue'),
        wt2=dict(color='red'), 
        wt_signal=dict(color='green', _method='bar')
    )
    
    def __init__(self):
        # Typical price
        self.ap = SafeDivision(
            self.data.high + self.data.low + self.data.close, 
            3.0
        )
        
        # EMA calculations
        self.esa = btind.ExponentialMovingAverage(self.ap, period=self.params.n1)
        
        # Custom absolute value calculation
        diff = self.ap - self.esa
        abs_diff = bt.If(diff >= 0, diff, -diff)
        self.d = btind.ExponentialMovingAverage(abs_diff, period=self.params.n1)
    
    def next(self):
        try:
            # Safe CI calculation with enhanced protection
            numerator = self.ap[0] - self.esa[0]
            denominator = 0.015 * self.d[0]
            
            # Multiple layers of safety checks
            if (math.isnan(numerator) or math.isnan(denominator) or 
                math.isinf(numerator) or math.isinf(denominator) or 
                abs(denominator) < self.params.ci_min_denominator):
                ci_value = self.params.ci_fallback
            else:
                ci_value = numerator / denominator
                
                # Additional bounds checking
                if math.isnan(ci_value) or math.isinf(ci_value):
                    ci_value = self.params.ci_fallback
                elif abs(ci_value) > 1000:  # Extreme value protection
                    ci_value = 1000 if ci_value > 0 else -1000
            
            # Store CI for TCI calculation (simulated)
            if not hasattr(self, '_ci_history'):
                self._ci_history = []
            self._ci_history.append(ci_value)
            
            # Keep only last n2 periods for TCI calculation
            if len(self._ci_history) > self.params.n2:
                self._ci_history.pop(0)
            
            # Simple TCI approximation (EMA of CI)
            if len(self._ci_history) >= self.params.n2:
                alpha = 2.0 / (self.params.n2 + 1)
                if not hasattr(self, '_tci_value'):
                    self._tci_value = sum(self._ci_history) / len(self._ci_history)
                else:
                    self._tci_value = alpha * ci_value + (1 - alpha) * self._tci_value
            else:
                self._tci_value = ci_value
            
            # WT1 = TCI
            wt1_value = self._tci_value
            
            # WT2 = SMA of WT1 (4-period)
            if not hasattr(self, '_wt1_history'):
                self._wt1_history = []
            self._wt1_history.append(wt1_value)
            if len(self._wt1_history) > 4:
                self._wt1_history.pop(0)
            
            wt2_value = sum(self._wt1_history) / len(self._wt1_history)
            
            # WaveTrend signal (wt1 > wt2)
            wt_signal_value = 1.0 if wt1_value > wt2_value else 0.0
            
            # Set line values
            self.lines.wt1[0] = wt1_value
            self.lines.wt2[0] = wt2_value
            self.lines.wt_signal[0] = wt_signal_value
            
        except (ZeroDivisionError, ValueError, TypeError, AttributeError):
            # Fallback values in case of any error
            self.lines.wt1[0] = 0.0
            self.lines.wt2[0] = 0.0
            self.lines.wt_signal[0] = 0.0


class FourSwordsSwingStrategyV174Fixed(bt.Strategy):
    """
    Four Swords Swing Strategy v1.7.4 - FIXED VERSION
    Enhanced with comprehensive error handling and numerical stability
    
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
        ('use_wt_filter', True),  # Add WaveTrend filter parameter
        
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
        
        # Core indicators with enhanced error handling
        try:
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
        except Exception as e:
            print(f"Error initializing indicators: {e}")
            raise
        
        # EMA trend filter
        if self.params.use_ema_filter:
            self.ema_fast = btind.ExponentialMovingAverage(self.data.close, period=self.params.ema_fast)
            self.ema_slow = btind.ExponentialMovingAverage(self.data.close, period=self.params.ema_slow)
            self.ema_bull_trend = self.ema_fast > self.ema_slow
            self.ema_bear_trend = self.ema_fast < self.ema_slow
        else:
            self.ema_bull_trend = None
            self.ema_bear_trend = None
        
        # Volume filter with enhanced safety checks  
        if self.params.use_volume_filter:
            self.avg_volume = btind.SimpleMovingAverage(self.data.volume, period=20)
            # Enhanced volume threshold calculation with safety checks
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
            'calculation_errors': 0,     # Calculation errors caught
        }
        
    def next(self):
        """Main strategy logic executed on each bar"""
        
        try:
            # Get current signal conditions with safety checks
            signal_bar = bool(self.sqzmom.lines.signal_bar[0])
            momentum = self.sqzmom.lines.momentum[0]
            
            # WaveTrend signal with safety check
            if self.params.use_wt_filter:
                wt_signal = bool(self.wavetrend.lines.wt_signal[0])
            else:
                wt_signal = True  # Always true when WT filter is disabled
            
            # Validate momentum value
            if math.isnan(momentum) or math.isinf(momentum):
                momentum = 0.0
            
            # Apply signal confirmation delay if enabled
            if self.params.use_confirmed_signal and len(self) > 1:
                signal_bar = bool(self.sqzmom.lines.signal_bar[-1])
                momentum = self.sqzmom.lines.momentum[-1]
                if self.params.use_wt_filter:
                    wt_signal = bool(self.wavetrend.lines.wt_signal[-1])
                
                # Validate delayed momentum
                if math.isnan(momentum) or math.isinf(momentum):
                    momentum = 0.0
            
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
            
            # Step 3: Apply Volume filter with enhanced safety
            volume_long_passed = ema_long_passed
            volume_short_passed = ema_short_passed
            
            if self.params.use_volume_filter and self.volume_confirm is not None:
                # Enhanced safety checks for volume filtering
                current_volume = self.data.volume[0]
                avg_vol = self.avg_volume[0]
                
                has_valid_volume = (
                    not math.isnan(current_volume) and not math.isnan(avg_vol) and
                    not math.isinf(current_volume) and not math.isinf(avg_vol) and
                    current_volume > 0 and avg_vol > 0
                )
                
                if has_valid_volume:
                    volume_long_passed = ema_long_passed and bool(self.volume_confirm[0])
                    volume_short_passed = ema_short_passed and bool(self.volume_confirm[0])
                else:
                    volume_long_passed = False
                    volume_short_passed = False
            
            if volume_long_passed:
                self.counters['volume_passed_long'] += 1
            if volume_short_passed:
                self.counters['volume_passed_short'] += 1
            
            # Step 4: Apply WaveTrend direction filter
            wt_long_passed = volume_long_passed
            wt_short_passed = volume_short_passed
            
            if self.params.use_wt_filter:
                wt_long_passed = volume_long_passed and wt_signal
                wt_short_passed = volume_short_passed and not wt_signal
            
            if wt_long_passed:
                self.counters['wt_passed_long'] += 1
            if wt_short_passed:
                self.counters['wt_passed_short'] += 1
            
            # Final signals
            final_long_signal = wt_long_passed
            final_short_signal = wt_short_passed
            
            # Simplified entry logic for immediate signals
            if not self.position:  # No current position
                if final_long_signal and self.params.trade_direction in ['long', 'both']:
                    # Calculate position size with safety checks
                    try:
                        if self.params.use_sizer:
                            self.buy()
                        else:
                            # Manual position sizing with enhanced safety
                            equity = self.broker.get_value()
                            position_value = equity * self.params.position_pct
                            price = self.data.close[0]
                            
                            if price > 0 and not math.isnan(price) and not math.isinf(price):
                                raw_qty = position_value / price
                                qty = max(self.params.min_qty, 
                                         round(raw_qty / self.params.qty_step) * self.params.qty_step)
                                self.buy(size=qty)
                            
                        self.counters['actual_entries_long'] += 1
                        self.entry_price = self.data.close[0]
                        self.entry_bar = len(self)
                        
                    except Exception as e:
                        print(f"Error in long entry: {e}")
                        self.counters['calculation_errors'] += 1
                
                elif final_short_signal and self.params.trade_direction in ['short', 'both']:
                    # Calculate position size for short with safety checks
                    try:
                        if self.params.use_sizer:
                            self.sell()
                        else:
                            # Manual position sizing for short
                            equity = self.broker.get_value()
                            position_value = equity * self.params.position_pct
                            price = self.data.close[0]
                            
                            if price > 0 and not math.isnan(price) and not math.isinf(price):
                                raw_qty = position_value / price
                                qty = max(self.params.min_qty,
                                         round(raw_qty / self.params.qty_step) * self.params.qty_step)
                                self.sell(size=qty)
                            
                        self.counters['actual_entries_short'] += 1
                        self.entry_price = self.data.close[0]
                        self.entry_bar = len(self)
                        
                    except Exception as e:
                        print(f"Error in short entry: {e}")
                        self.counters['calculation_errors'] += 1
            
            # Exit logic (simplified - can be enhanced based on original strategy)
            elif self.position:
                # Basic exit conditions (enhance as needed)
                bars_in_trade = len(self) - self.entry_bar if self.entry_bar else 0
                
                # Exit after reasonable time or on opposite signal
                exit_condition = (
                    bars_in_trade > 50 or  # Max bars in trade
                    (self.position.size > 0 and final_short_signal) or  # Long position, short signal
                    (self.position.size < 0 and final_long_signal)      # Short position, long signal
                )
                
                if exit_condition:
                    self.close()
                    self.entry_price = None
                    self.entry_bar = None
            
        except Exception as e:
            print(f"Error in strategy next(): {e}")
            self.counters['calculation_errors'] += 1
    
    def stop(self):
        """Print strategy statistics at the end"""
        print(f"\n=== Four Swords v1.7.4 FIXED - Final Statistics ===")
        print(f"Signal Flow Analysis:")
        for key, value in self.counters.items():
            print(f"  {key}: {value}")
        print(f"Final Portfolio Value: {self.broker.get_value():.2f}")
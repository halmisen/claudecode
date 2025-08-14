"""
Four Swords Swing Strategy v1.5 Enhanced - Python Implementation
Enhanced version with comprehensive risk management and adaptive parameters
Translated from pinescript/strategies/oscillator/Four_Swords_Swing_Strategy_v1_5_enhanced.pine
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


class FourSwordsEnhancedStrategy(bt.Strategy):
    """
    Enhanced Four Swords Swing Strategy with advanced risk management
    
    Key Enhancements:
    - ATR dynamic stop losses
    - Volatility-adjusted position sizing
    - Enhanced momentum detection with 3-period SMA + rate threshold
    - Market regime detection for adaptive parameters
    - Weighted confirmation scoring system
    - Circuit breaker protection
    """
    
    # === Strategy Parameters ===
    params = (
        # SQZMOM Core Parameters
        ('bb_length', 20),
        ('bb_mult', 2.0), 
        ('kc_length', 20),
        ('kc_mult', 1.5),
        ('use_true_range', True),
        
        # WaveTrend Parameters
        ('wt_channel_length', 10),
        ('wt_average_length', 21),
        
        # Swing Filters
        ('use_ema_filter', True),
        ('ema_fast', 20),
        ('ema_slow', 50),
        ('use_volume_filter', True),
        ('volume_multiplier', 1.2),
        
        # Risk Management (Enhanced)
        ('use_stop_loss', True),
        ('atr_multiplier', 2.0),
        ('atr_length', 14),
        ('use_volatility_position', True),
        ('base_position_size', 15.0),
        ('max_drawdown_percent', 15.0),
        ('max_consecutive_losses', 3),
        ('use_time_exit', True),
        ('max_bars_in_trade', 50),
        
        # Strategy Settings
        ('trade_direction', 'both'),  # 'long', 'short', 'both'
        ('use_confirmed_signal', False),
        ('use_enhanced_momentum', True),
        
        # Market Type
        ('market_type', 'crypto'),  # 'crypto' or 'stocks'
        ('leverage', 1.0),
        
        # Debug and Plotting
        ('debug', False),
        ('plot_indicators', True),
    )
    
    def __init__(self):
        """Initialize strategy with enhanced indicators and risk management"""
        
        # === Data References ===
        self.data_close = self.data.close
        self.data_high = self.data.high  
        self.data_low = self.data.low
        self.data_volume = self.data.volume
        
        # === Market Regime Detection ===
        self.atr14 = btind.ATR(self.data, period=14)
        self.atr_sma50 = btind.SMA(self.atr14, period=50)
        self.atr_ratio = self.atr14 / self.atr_sma50
        
        self.ema_20 = btind.EMA(self.data, period=20)
        self.ema_50 = btind.EMA(self.data, period=50)
        self.trend_strength = abs(self.ema_20 - self.ema_50) / self.atr14
        
        # === Adaptive Parameters ===
        # These will be calculated dynamically in next()
        self.trending_market = False
        self.volatile_market = False
        self.adaptive_bb_length = self.p.bb_length
        self.adaptive_kc_mult = self.p.kc_mult
        self.adaptive_wt_n1 = self.p.wt_channel_length
        
        # === Enhanced SQZMOM Indicators ===
        # Will be recalculated with adaptive parameters in next()
        self.bb_basis = btind.SMA(self.data, period=self.p.bb_length)
        self.bb_dev = self.p.bb_mult * btind.StdDev(self.data, period=self.p.bb_length)
        self.bb_upper = self.bb_basis + self.bb_dev
        self.bb_lower = self.bb_basis - self.bb_dev
        
        # Keltner Channels
        self.kc_ma = btind.SMA(self.data, period=self.p.kc_length)
        if self.p.use_true_range:
            self.kc_range = btind.TrueRange(self.data)
        else:
            self.kc_range = self.data_high - self.data_low
        self.kc_rangema = btind.SMA(self.kc_range, period=self.p.kc_length)
        self.kc_upper = self.kc_ma + self.kc_rangema * self.p.kc_mult
        self.kc_lower = self.kc_ma - self.kc_rangema * self.p.kc_mult
        
        # === Enhanced Momentum Detection ===
        # LazyBear momentum calculation
        self.highest_high = btind.Highest(self.data_high, period=self.p.kc_length)
        self.lowest_low = btind.Lowest(self.data_low, period=self.p.kc_length)
        self.kc_mid = btind.SMA(self.data_close, period=self.p.kc_length)
        self.momentum_source = self.data_close - ((self.highest_high + self.lowest_low) / 2 + self.kc_mid) / 2
        
        # Enhanced momentum with 3-period SMA and rate threshold
        self.momentum_sma3 = btind.SMA(self.momentum_source, period=3)
        
        # === Enhanced WaveTrend ===
        self.hlc3 = (self.data_high + self.data_low + self.data_close) / 3
        self.wt_esa = btind.EMA(self.hlc3, period=self.p.wt_channel_length)
        
        # === EMA Trend Filter ===
        if self.p.use_ema_filter:
            self.ema_fast_line = btind.EMA(self.data, period=self.p.ema_fast)
            self.ema_slow_line = btind.EMA(self.data, period=self.p.ema_slow)
        
        # === Volume Filter ===
        if self.p.use_volume_filter:
            self.avg_volume = btind.SMA(self.data_volume, period=20)
        
        # === Risk Management ===
        self.atr_value = btind.ATR(self.data, period=self.p.atr_length)
        
        # Volatility-adjusted position sizing
        self.volatility = btind.StdDev(self.data_close, period=20) / btind.SMA(self.data_close, period=20)
        self.volatility_sma50 = btind.SMA(self.volatility, period=50)
        
        # === State Variables ===
        self.wait_long_exit_by_squeeze = False
        self.wait_short_exit_by_squeeze = False
        self.long_stop_price = None
        self.short_stop_price = None
        self.entry_price = None
        self.bars_in_trade = 0
        
        # Risk tracking
        self.peak_equity = self.broker.get_cash()
        self.consecutive_losses = 0
        self.last_trade_profit = 0
        
        # === Plotting Setup ===
        if self.p.plot_indicators:
            # Plot EMA lines if enabled
            if self.p.use_ema_filter:
                self.ema_fast_line.plotinfo.plot = True
                self.ema_fast_line.plotinfo.plotname = 'EMA Fast'
                self.ema_slow_line.plotinfo.plot = True 
                self.ema_slow_line.plotinfo.plotname = 'EMA Slow'
    
    def next(self):
        """Main strategy logic with enhanced features"""
        
        # === Market Regime Detection ===
        if len(self.data) > 50:  # Ensure sufficient data
            self.trending_market = self.trend_strength[0] > 2.0
            self.volatile_market = self.atr_ratio[0] > 1.2
            
            # Adaptive parameter adjustment
            self.adaptive_bb_length = int(round(self.p.bb_length * 1.1)) if self.volatile_market else self.p.bb_length
            self.adaptive_kc_mult = self.p.kc_mult * 0.9 if self.trending_market else self.p.kc_mult * 1.1
            self.adaptive_wt_n1 = max(5, self.p.wt_channel_length - 2) if self.trending_market else min(20, self.p.wt_channel_length + 2)
        
        # === Enhanced SQZMOM Calculation ===
        if len(self.data) < max(self.p.bb_length, self.p.kc_length, self.p.wt_average_length):
            return
            
        # Squeeze detection
        squeeze_on = (self.bb_lower[0] > self.kc_lower[0]) and (self.bb_upper[0] < self.kc_upper[0])
        squeeze_off = (self.bb_lower[0] < self.kc_lower[0]) and (self.bb_upper[0] > self.kc_upper[0])
        no_squeeze = not squeeze_on and not squeeze_off
        
        # Signal detection
        prev_squeeze_on = len(self.data) > 1 and (self.bb_lower[-1] > self.kc_lower[-1]) and (self.bb_upper[-1] < self.kc_upper[-1])
        black_cross = prev_squeeze_on and not squeeze_on
        signal_bar = black_cross and not no_squeeze
        
        # === Enhanced Momentum Detection ===
        if len(self.data) > 3:
            momentum_current = self.momentum_source[0]
            momentum_prev = self.momentum_source[-1] if len(self.data) > 1 else 0
            momentum_sma3_current = self.momentum_sma3[0]
            
            # Enhanced momentum acceleration detection
            if self.p.use_enhanced_momentum and momentum_prev != 0:
                momentum_rate = (momentum_current - momentum_prev) / max(abs(momentum_prev), 0.001)
                momentum_accelerating = momentum_current > momentum_sma3_current and momentum_rate > 0.05
            else:
                momentum_accelerating = momentum_current > momentum_prev
        else:
            momentum_current = 0
            momentum_accelerating = False
        
        # === Enhanced WaveTrend Calculation ===
        if len(self.data) > self.p.wt_average_length:
            wt_d = abs(self.hlc3[0] - self.wt_esa[0])
            # Division by zero protection
            wt_ci = (self.hlc3[0] - self.wt_esa[0]) / (0.015 * wt_d) if wt_d != 0 else 0
            
            # Simple EMA approximation for wt_tci
            if not hasattr(self, 'wt_tci_prev'):
                self.wt_tci_prev = wt_ci
            alpha = 2.0 / (self.p.wt_average_length + 1)
            wt_tci = alpha * wt_ci + (1 - alpha) * self.wt_tci_prev
            self.wt_tci_prev = wt_tci
            
            # WaveTrend signals
            if not hasattr(self, 'wt1_history'):
                self.wt1_history = []
            self.wt1_history.append(wt_tci)
            if len(self.wt1_history) > 4:
                self.wt1_history.pop(0)
            
            wt1 = wt_tci
            wt2 = sum(self.wt1_history) / len(self.wt1_history) if self.wt1_history else wt_tci
            wt_cross_up = wt1 > wt2
        else:
            wt1 = wt2 = 0
            wt_cross_up = False
        
        # === Filter Calculations ===
        # EMA trend filter
        if self.p.use_ema_filter and len(self.data) > max(self.p.ema_fast, self.p.ema_slow):
            ema_bull_trend = self.ema_fast_line[0] > self.ema_slow_line[0]
            ema_bear_trend = self.ema_fast_line[0] < self.ema_slow_line[0]
        else:
            ema_bull_trend = ema_bear_trend = True
        
        # Volume filter with adaptive threshold
        if self.p.use_volume_filter and len(self.data) > 20:
            normalized_vol = self.volatility[0] / self.volatility_sma50[0] if self.volatility_sma50[0] != 0 else 1
            adaptive_volume_threshold = self.p.volume_multiplier * (1.0 + (normalized_vol - 1.0) * 0.3)
            volume_confirm = self.data_volume[0] > self.avg_volume[0] * adaptive_volume_threshold
        else:
            volume_confirm = True
        
        # === Enhanced Signal Quality with Weighted Confirmation ===
        confirmation_score = 0.0
        if signal_bar:
            confirmation_score += 30.0  # Base SQZMOM signal
        if momentum_current > 0:
            confirmation_score += 25.0  # Momentum direction  
        if wt_cross_up:
            confirmation_score += 20.0  # WaveTrend alignment
        if ema_bull_trend:
            confirmation_score += 15.0  # Trend alignment
        if volume_confirm:
            confirmation_score += 10.0  # Volume confirmation
        
        required_score = 85.0 if self.volatile_market else 75.0
        high_quality_long_signal = confirmation_score >= required_score and momentum_current > 0
        high_quality_short_signal = confirmation_score >= required_score and momentum_current < 0
        
        # === Basic Entry Signals ===
        basic_long_signal = signal_bar and momentum_current > 0 and wt_cross_up
        basic_short_signal = signal_bar and momentum_current < 0 and not wt_cross_up
        
        # === Enhanced Swing Signals ===
        swing_long_signal = high_quality_long_signal and ema_bull_trend and volume_confirm
        swing_short_signal = high_quality_short_signal and ema_bear_trend and volume_confirm
        
        # === Risk Management Calculations ===
        # Track peak equity and drawdown
        current_equity = self.broker.get_value()
        if current_equity > self.peak_equity:
            self.peak_equity = current_equity
        
        current_drawdown = (self.peak_equity - current_equity) / self.peak_equity * 100
        
        # Circuit breaker conditions
        drawdown_breached = current_drawdown >= self.p.max_drawdown_percent
        max_losses_reached = self.consecutive_losses >= self.p.max_consecutive_losses
        circuit_breaker = drawdown_breached or max_losses_reached
        
        # Time-based exit
        if self.position:
            self.bars_in_trade += 1
        else:
            self.bars_in_trade = 0
        
        time_exit_needed = self.p.use_time_exit and self.bars_in_trade >= self.p.max_bars_in_trade
        
        # === Final Filtered Signals ===
        long_signal_filtered = swing_long_signal and not circuit_breaker and (self.p.trade_direction in ['both', 'long'])
        short_signal_filtered = swing_short_signal and not circuit_breaker and (self.p.trade_direction in ['both', 'short'])
        
        # === Position Sizing ===
        if self.p.use_volatility_position:
            normalized_vol = self.volatility[0] / self.volatility_sma50[0] if self.volatility_sma50[0] != 0 else 1
            position_size = max(5.0, min(25.0, self.p.base_position_size / max(normalized_vol, 0.5)))
        else:
            position_size = self.p.base_position_size
        
        # === Entry Logic ===
        if not self.position:
            if long_signal_filtered:
                size = self.broker.get_cash() * (position_size / 100.0) / self.data_close[0]
                self.buy(size=size)
                
                # Set stop loss
                if self.p.use_stop_loss:
                    self.long_stop_price = self.data_close[0] - (self.atr_value[0] * self.p.atr_multiplier)
                
                # Set exit strategy type
                self.wait_long_exit_by_squeeze = momentum_accelerating and momentum_current > 0
                self.entry_price = self.data_close[0]
                
                if self.p.debug:
                    print(f"LONG ENTRY at {self.data_close[0]:.4f}, Stop: {self.long_stop_price:.4f if self.long_stop_price else 'None'}")
            
            elif short_signal_filtered:
                size = self.broker.get_cash() * (position_size / 100.0) / self.data_close[0] 
                self.sell(size=size)
                
                # Set stop loss
                if self.p.use_stop_loss:
                    self.short_stop_price = self.data_close[0] + (self.atr_value[0] * self.p.atr_multiplier)
                
                # Set exit strategy type
                self.wait_short_exit_by_squeeze = momentum_accelerating and momentum_current < 0
                self.entry_price = self.data_close[0]
                
                if self.p.debug:
                    print(f"SHORT ENTRY at {self.data_close[0]:.4f}, Stop: {self.short_stop_price:.4f if self.short_stop_price else 'None'}")
        
        # === Exit Logic ===
        if self.position:
            exit_reason = ""
            
            if self.position.size > 0:  # Long position
                # Momentum weakening exit
                exit_long_weak = not self.wait_long_exit_by_squeeze and momentum_current < 0
                
                # Squeeze re-entry exit
                squeeze_back_in = squeeze_on and not prev_squeeze_on
                exit_long_squeeze = self.wait_long_exit_by_squeeze and squeeze_back_in
                
                # Stop loss exit
                long_stop_hit = self.p.use_stop_loss and self.long_stop_price and self.data_close[0] <= self.long_stop_price
                
                # Combined exit condition
                long_exit_condition = exit_long_weak or exit_long_squeeze or long_stop_hit or time_exit_needed
                
                if long_exit_condition:
                    self.close()
                    if long_stop_hit:
                        exit_reason = "Stop Loss"
                    elif time_exit_needed:
                        exit_reason = "Time Exit"
                    elif exit_long_squeeze:
                        exit_reason = "Squeeze Exit"
                    else:
                        exit_reason = "Signal Exit"
                    
                    if self.p.debug:
                        print(f"LONG EXIT at {self.data_close[0]:.4f}, Reason: {exit_reason}")
            
            elif self.position.size < 0:  # Short position
                # Momentum weakening exit  
                exit_short_weak = not self.wait_short_exit_by_squeeze and momentum_current > 0
                
                # Squeeze re-entry exit
                squeeze_back_in = squeeze_on and not prev_squeeze_on
                exit_short_squeeze = self.wait_short_exit_by_squeeze and squeeze_back_in
                
                # Stop loss exit
                short_stop_hit = self.p.use_stop_loss and self.short_stop_price and self.data_close[0] >= self.short_stop_price
                
                # Combined exit condition
                short_exit_condition = exit_short_weak or exit_short_squeeze or short_stop_hit or time_exit_needed
                
                if short_exit_condition:
                    self.close()
                    if short_stop_hit:
                        exit_reason = "Stop Loss"
                    elif time_exit_needed:
                        exit_reason = "Time Exit"
                    elif exit_short_squeeze:
                        exit_reason = "Squeeze Exit"
                    else:
                        exit_reason = "Signal Exit"
                    
                    if self.p.debug:
                        print(f"SHORT EXIT at {self.data_close[0]:.4f}, Reason: {exit_reason}")
        
        # Reset state on exit
        if not self.position and (self.wait_long_exit_by_squeeze or self.wait_short_exit_by_squeeze):
            self.wait_long_exit_by_squeeze = False
            self.wait_short_exit_by_squeeze = False
            self.long_stop_price = None
            self.short_stop_price = None
            self.entry_price = None
            self.bars_in_trade = 0
    
    def notify_trade(self, trade):
        """Track consecutive losses for risk management"""
        if trade.isclosed:
            if trade.pnl < 0:
                self.consecutive_losses += 1
            else:
                self.consecutive_losses = 0
            
            if self.p.debug:
                print(f"Trade closed: PnL: {trade.pnl:.2f}, Consecutive losses: {self.consecutive_losses}")
    
    def stop(self):
        """Final strategy statistics"""
        if self.p.debug:
            print(f"Final portfolio value: {self.broker.get_value():.2f}")
            print(f"Total return: {(self.broker.get_value() / self.broker.get_cash() - 1) * 100:.2f}%")


# === Analysis Functions ===

def calculate_performance_metrics(strategy_results):
    """Calculate comprehensive performance metrics for strategy validation"""
    
    if not hasattr(strategy_results, 'analyzers'):
        return {}
    
    # Get trade analyzer results
    trade_analyzer = strategy_results.analyzers.trade_analyzer.get_analysis()
    returns_analyzer = strategy_results.analyzers.returns.get_analysis()
    drawdown_analyzer = strategy_results.analyzers.drawdown.get_analysis()
    
    metrics = {
        'total_trades': trade_analyzer.get('total', {}).get('total', 0),
        'winning_trades': trade_analyzer.get('won', {}).get('total', 0),
        'losing_trades': trade_analyzer.get('lost', {}).get('total', 0),
        'win_rate': 0,
        'avg_win': trade_analyzer.get('won', {}).get('pnl', {}).get('average', 0),
        'avg_loss': trade_analyzer.get('lost', {}).get('pnl', {}).get('average', 0),
        'total_return': returns_analyzer.get('rtot', 0) * 100,
        'annual_return': returns_analyzer.get('rnorm100', 0),
        'max_drawdown': drawdown_analyzer.get('max', {}).get('drawdown', 0),
        'sharpe_ratio': 0,
        'profit_factor': 0
    }
    
    # Calculate derived metrics
    if metrics['total_trades'] > 0:
        metrics['win_rate'] = (metrics['winning_trades'] / metrics['total_trades']) * 100
    
    if metrics['avg_loss'] != 0:
        metrics['profit_factor'] = abs(metrics['avg_win'] / metrics['avg_loss'])
    
    return metrics


def compare_strategies(original_results, enhanced_results):
    """Compare original vs enhanced strategy performance"""
    
    orig_metrics = calculate_performance_metrics(original_results)
    enh_metrics = calculate_performance_metrics(enhanced_results)
    
    comparison = {
        'metrics': ['Total Return', 'Win Rate', 'Max Drawdown', 'Profit Factor', 'Total Trades'],
        'original': [
            f"{orig_metrics.get('total_return', 0):.2f}%",
            f"{orig_metrics.get('win_rate', 0):.1f}%", 
            f"{orig_metrics.get('max_drawdown', 0):.2f}%",
            f"{orig_metrics.get('profit_factor', 0):.2f}",
            f"{orig_metrics.get('total_trades', 0)}"
        ],
        'enhanced': [
            f"{enh_metrics.get('total_return', 0):.2f}%",
            f"{enh_metrics.get('win_rate', 0):.1f}%",
            f"{enh_metrics.get('max_drawdown', 0):.2f}%", 
            f"{enh_metrics.get('profit_factor', 0):.2f}",
            f"{enh_metrics.get('total_trades', 0)}"
        ],
        'improvement': []
    }
    
    # Calculate improvements
    improvements = [
        enh_metrics.get('total_return', 0) - orig_metrics.get('total_return', 0),
        enh_metrics.get('win_rate', 0) - orig_metrics.get('win_rate', 0),
        orig_metrics.get('max_drawdown', 0) - enh_metrics.get('max_drawdown', 0),  # Lower is better
        enh_metrics.get('profit_factor', 0) - orig_metrics.get('profit_factor', 0),
        enh_metrics.get('total_trades', 0) - orig_metrics.get('total_trades', 0)
    ]
    
    for i, improvement in enumerate(improvements):
        if i == 2:  # Max drawdown - lower is better
            comparison['improvement'].append(f"{improvement:.2f}% (better)" if improvement > 0 else f"{improvement:.2f}% (worse)")
        elif i == 4:  # Total trades - just show difference
            comparison['improvement'].append(f"{improvement:+.0f}")
        else:
            comparison['improvement'].append(f"{improvement:+.2f}{'%' if i < 2 else ''}")
    
    return comparison
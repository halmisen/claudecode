"""
SQZMOM + WaveTrend Strategy for Jesse Framework
Converted from SQZMOM_WaveTrend_Strategy.PINE
"""

import numpy as np
import pandas as pd
from jesse import utils
from jesse.strategies import Strategy
from jesse.indicators import sma, ema, stdev
from ..indicators.technical_indicators import (
    squeeze_momentum, wavetrend, get_momentum_color,
    trange, highest, lowest, linreg
)


class SQZMOMWaveTrendStrategy(Strategy):
    """
    Squeeze Momentum + WaveTrend Strategy
    
    Strategy Logic:
    - Uses Squeeze Momentum indicator to identify squeeze breakouts
    - Confirms signals with WaveTrend indicator
    - Sophisticated exit logic based on momentum strength or squeeze re-entry
    - Optional stop loss functionality
    """
    
    def __init__(self):
        super().__init__()
        
        # Strategy state variables
        self.wait_long_exit_by_squeeze = False
        self.wait_short_exit_by_squeeze = False
        
        # Previous values for state tracking
        self.prev_sqz_on = False
        self.prev_momentum = None
        self.prev_momentum_color = None
        
    # === Inputs ===
    @property
    def bb_length(self):
        return self.candles[0].get_config('bb_length', 20)
    
    @property
    def bb_mult(self):
        return self.candles[0].get_config('bb_mult', 2.0)
    
    @property
    def kc_length(self):
        return self.candles[0].get_config('kc_length', 20)
    
    @property
    def kc_mult(self):
        return self.candles[0].get_config('kc_mult', 1.5)
    
    @property
    def use_true_range(self):
        return self.candles[0].get_config('use_true_range', True)
    
    @property
    def use_confirmed_signal(self):
        return self.candles[0].get_config('use_confirmed_signal', False)
    
    @property
    def wt_channel_length(self):
        return self.candles[0].get_config('wt_channel_length', 10)
    
    @property
    def wt_avg_length(self):
        return self.candles[0].get_config('wt_avg_length', 21)
    
    @property
    def trade_direction(self):
        return self.candles[0].get_config('trade_direction', 'both')
    
    @property
    def use_stop_loss(self):
        return self.candles[0].get_config('use_stop_loss', False)
    
    @property
    def stop_loss_percent(self):
        return self.candles[0].get_config('stop_loss_percent', 2.0)
    
    def prepare_data(self):
        """Prepare indicator data before strategy execution"""
        # Get OHLC data
        close = self.candles[:, 2]
        high = self.candles[:, 3]
        low = self.candles[:, 4]
        
        # Calculate Squeeze Momentum
        self.sqz_on, self.sqz_off, self.no_sqz, self.momentum = squeeze_momentum(
            high, low, close,
            self.bb_length, self.bb_mult,
            self.kc_length, self.kc_mult,
            self.use_true_range
        )
        
        # Calculate WaveTrend
        hlc3 = (high + low + close) / 3
        self.wt1, self.wt2 = wavetrend(hlc3, self.wt_channel_length, self.wt_avg_length)
        
        # Get momentum colors
        self.momentum_color = get_momentum_color(self.momentum)
        
        # Store previous values for signal confirmation
        if len(self.candles) > 1:
            self.prev_sqz_on = self.sqz_on[-2] if len(self.sqz_on) > 1 else False
            self.prev_momentum = self.momentum[-2] if len(self.momentum) > 1 else None
            self.prev_momentum_color = self.momentum_color[-2] if len(self.momentum_color) > 1 else None
    
    def should_long(self) -> bool:
        """Determine if we should enter a long position"""
        if self.trade_direction == 'short_only':
            return False
        
        # Get current values
        current_sqz_on = self.sqz_on[-1]
        current_momentum = self.momentum[-1]
        current_wt1 = self.wt1[-1]
        current_wt2 = self.wt2[-1]
        
        # Black cross signal (squeeze release)
        black_cross_raw = self.prev_sqz_on and not current_sqz_on
        signal_bar_raw = black_cross_raw and not self.no_sqz[-1]
        
        # Apply confirmation delay if enabled
        if self.use_confirmed_signal:
            # Need to check previous bar for confirmation
            if len(self.candles) < 3:
                return False
            black_cross = self.sqz_on[-3] and not self.prev_sqz_on
            signal_bar = black_cross and not self.no_sqz[-2]
        else:
            black_cross = black_cross_raw
            signal_bar = signal_bar_raw
        
        # Long signal conditions
        long_signal = (signal_bar and 
                      current_momentum > 0 and 
                      current_wt1 > current_wt2)
        
        return long_signal
    
    def should_short(self) -> bool:
        """Determine if we should enter a short position"""
        if self.trade_direction == 'long_only':
            return False
        
        # Get current values
        current_sqz_on = self.sqz_on[-1]
        current_momentum = self.momentum[-1]
        current_wt1 = self.wt1[-1]
        current_wt2 = self.wt2[-1]
        
        # Black cross signal (squeeze release)
        black_cross_raw = self.prev_sqz_on and not current_sqz_on
        signal_bar_raw = black_cross_raw and not self.no_sqz[-1]
        
        # Apply confirmation delay if enabled
        if self.use_confirmed_signal:
            # Need to check previous bar for confirmation
            if len(self.candles) < 3:
                return False
            black_cross = self.sqz_on[-3] and not self.prev_sqz_on
            signal_bar = black_cross and not self.no_sqz[-2]
        else:
            black_cross = black_cross_raw
            signal_bar = signal_bar_raw
        
        # Short signal conditions
        short_signal = (signal_bar and 
                       current_momentum < 0 and 
                       current_wt1 < current_wt2)
        
        return short_signal
    
    def should_cancel_entry(self) -> bool:
        """Determine if we should cancel a pending entry"""
        return False
    
    def go_long(self):
        """Execute long entry"""
        # Set exit condition state
        current_momentum_color = self.momentum_color[-1]
        self.wait_long_exit_by_squeeze = (current_momentum_color == 'green')
        
        # Calculate position size based on risk
        qty = utils.size_to_qty(
            self.capital * 0.2,  # 20% of capital per trade
            self.price,
            fee_rate=0.001
        )
        
        # Enter long position
        self.buy = qty, self.price
        
        # Set stop loss if enabled
        if self.use_stop_loss:
            stop_price = self.price * (1 - self.stop_loss_percent / 100)
            self.stop_loss = qty, stop_price
    
    def go_short(self):
        """Execute short entry"""
        # Set exit condition state
        current_momentum_color = self.momentum_color[-1]
        self.wait_short_exit_by_squeeze = (current_momentum_color == 'maroon')
        
        # Calculate position size based on risk
        qty = utils.size_to_qty(
            self.capital * 0.2,  # 20% of capital per trade
            self.price,
            fee_rate=0.001
        )
        
        # Enter short position
        self.sell = qty, self.price
        
        # Set stop loss if enabled
        if self.use_stop_loss:
            stop_price = self.price * (1 + self.stop_loss_percent / 100)
            self.stop_loss = qty, stop_price
    
    def update_position(self):
        """Update open position"""
        if self.is_long:
            self._update_long_position()
        elif self.is_short:
            self._update_short_position()
    
    def _update_long_position(self):
        """Update long position exit logic"""
        current_sqz_on = self.sqz_on[-1]
        current_momentum_color = self.momentum_color[-1]
        
        # Check for squeeze re-entry
        squeeze_back_in = current_sqz_on and not self.prev_sqz_on
        
        # Exit conditions
        exit_long_weak = (not self.wait_long_exit_by_squeeze and 
                         current_momentum_color == 'green' and 
                         self.prev_momentum_color == 'lime')
        
        exit_long_squeeze = (self.wait_long_exit_by_squeeze and squeeze_back_in)
        
        # Exit if either condition is met
        if exit_long_weak or exit_long_squeeze:
            self.liquidate()
            # Reset state
            self.wait_long_exit_by_squeeze = False
            self.wait_short_exit_by_squeeze = False
    
    def _update_short_position(self):
        """Update short position exit logic"""
        current_sqz_on = self.sqz_on[-1]
        current_momentum_color = self.momentum_color[-1]
        
        # Check for squeeze re-entry
        squeeze_back_in = current_sqz_on and not self.prev_sqz_on
        
        # Exit conditions
        exit_short_weak = (not self.wait_short_exit_by_squeeze and 
                          current_momentum_color == 'maroon' and 
                          self.prev_momentum_color == 'red')
        
        exit_short_squeeze = (self.wait_short_exit_by_squeeze and squeeze_back_in)
        
        # Exit if either condition is met
        if exit_short_weak or exit_short_squeeze:
            self.liquidate()
            # Reset state
            self.wait_long_exit_by_squeeze = False
            self.wait_short_exit_by_squeeze = False
    
    def on_stop_loss(self, order):
        """Handle stop loss trigger"""
        # Reset state on stop loss
        self.wait_long_exit_by_squeeze = False
        self.wait_short_exit_by_squeeze = False
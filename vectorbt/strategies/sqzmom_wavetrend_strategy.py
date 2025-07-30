"""
SQZMOM + WaveTrend Strategy for VectorBT Framework
Converted from SQZMOM_WaveTrend_Strategy.PINE
"""

import numpy as np
import pandas as pd
import vectorbt as vbt
from typing import Dict, Any, Optional, Tuple

from ..indicators.technical_indicators import (
    squeeze_momentum, wavetrend, get_momentum_color
)


class SQZMOMWaveTrendStrategy:
    """
    Squeeze Momentum + WaveTrend Strategy for VectorBT
    
    Strategy Logic:
    - Uses Squeeze Momentum indicator to identify squeeze breakouts
    - Confirms signals with WaveTrend indicator
    - Sophisticated exit logic based on momentum strength or squeeze re-entry
    - Optional stop loss functionality
    """
    
    def __init__(self, 
                 bb_length: int = 20,
                 bb_mult: float = 2.0,
                 kc_length: int = 20,
                 kc_mult: float = 1.5,
                 use_true_range: bool = True,
                 use_confirmed_signal: bool = False,
                 wt_channel_length: int = 10,
                 wt_avg_length: int = 21,
                 trade_direction: str = 'both',
                 use_stop_loss: bool = False,
                 stop_loss_percent: float = 2.0,
                 initial_capital: float = 500,
                 position_size: float = 0.2):
        """
        Initialize strategy parameters
        
        Args:
            bb_length: Bollinger Bands length
            bb_mult: Bollinger Bands multiplier
            kc_length: Keltner Channels length
            kc_mult: Keltner Channels multiplier
            use_true_range: Use True Range for Keltner Channels
            use_confirmed_signal: Use 1-bar delay for signal confirmation
            wt_channel_length: WaveTrend channel length
            wt_avg_length: WaveTrend average length
            trade_direction: 'long_only', 'short_only', or 'both'
            use_stop_loss: Enable stop loss
            stop_loss_percent: Stop loss percentage
            initial_capital: Initial capital for backtesting
            position_size: Position size as fraction of capital
        """
        self.params = {
            'bb_length': bb_length,
            'bb_mult': bb_mult,
            'kc_length': kc_length,
            'kc_mult': kc_mult,
            'use_true_range': use_true_range,
            'use_confirmed_signal': use_confirmed_signal,
            'wt_channel_length': wt_channel_length,
            'wt_avg_length': wt_avg_length,
            'trade_direction': trade_direction,
            'use_stop_loss': use_stop_loss,
            'stop_loss_percent': stop_loss_percent,
            'initial_capital': initial_capital,
            'position_size': position_size
        }
        
    def calculate_indicators(self, high: pd.Series, low: pd.Series, close: pd.Series) -> Dict[str, pd.Series]:
        """
        Calculate all indicators needed for the strategy
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            
        Returns:
            Dictionary with all indicator series
        """
        # Calculate Squeeze Momentum
        sqz_on, sqz_off, no_sqz, momentum = squeeze_momentum(
            high, low, close,
            self.params['bb_length'], self.params['bb_mult'],
            self.params['kc_length'], self.params['kc_mult'],
            self.params['use_true_range']
        )
        
        # Calculate WaveTrend
        hlc3 = (high + low + close) / 3
        wt1, wt2 = wavetrend(hlc3, self.params['wt_channel_length'], self.params['wt_avg_length'])
        
        # Get momentum colors
        momentum_color = get_momentum_color(momentum)
        
        return {
            'sqz_on': sqz_on,
            'sqz_off': sqz_off,
            'no_sqz': no_sqz,
            'momentum': momentum,
            'wt1': wt1,
            'wt2': wt2,
            'momentum_color': momentum_color
        }
    
    def generate_signals(self, indicators: Dict[str, pd.Series]) -> Tuple[pd.Series, pd.Series]:
        """
        Generate entry and exit signals
        
        Args:
            indicators: Dictionary with all indicator series
            
        Returns:
            Tuple of (long_entries, long_exits, short_entries, short_exits)
        """
        sqz_on = indicators['sqz_on']
        momentum = indicators['momentum']
        wt1 = indicators['wt1']
        wt2 = indicators['wt2']
        momentum_color = indicators['momentum_color']
        no_sqz = indicators['no_sqz']
        
        # Previous values
        prev_sqz_on = sqz_on.shift(1)
        prev_momentum_color = momentum_color.shift(1)
        
        # Black cross signal (squeeze release)
        black_cross_raw = prev_sqz_on & ~sqz_on
        signal_bar_raw = black_cross_raw & ~no_sqz
        
        # Apply confirmation delay if enabled
        if self.params['use_confirmed_signal']:
            black_cross = sqz_on.shift(2) & ~prev_sqz_on
            signal_bar = black_cross & ~no_sqz.shift(1)
        else:
            black_cross = black_cross_raw
            signal_bar = signal_bar_raw
        
        # Long signals
        long_condition = (signal_bar & 
                         (momentum > 0) & 
                         (wt1 > wt2))
        
        # Short signals
        short_condition = (signal_bar & 
                          (momentum < 0) & 
                          (wt1 < wt2))
        
        # Filter by trade direction
        if self.params['trade_direction'] == 'long_only':
            long_entries = long_condition
            short_entries = pd.Series(False, index=long_entries.index)
        elif self.params['trade_direction'] == 'short_only':
            long_entries = pd.Series(False, index=long_entries.index)
            short_entries = short_condition
        else:  # both
            long_entries = long_condition
            short_entries = short_condition
        
        # State tracking for exits
        wait_long_exit_by_squeeze = pd.Series(False, index=long_entries.index)
        wait_short_exit_by_squeeze = pd.Series(False, index=long_entries.index)
        
        # On long entry, set exit condition
        for i in range(1, len(long_entries)):
            if long_entries.iloc[i] and not long_entries.iloc[:i].any():
                wait_long_exit_by_squeeze.iloc[i:] = (momentum_color.iloc[i] == 'green')
        
        # On short entry, set exit condition
        for i in range(1, len(short_entries)):
            if short_entries.iloc[i] and not short_entries.iloc[:i].any():
                wait_short_exit_by_squeeze.iloc[i:] = (momentum_color.iloc[i] == 'maroon')
        
        # Squeeze re-entry condition
        squeeze_back_in = sqz_on & ~prev_sqz_on
        
        # Long exit conditions
        exit_long_weak = (~wait_long_exit_by_squeeze & 
                         (momentum_color == 'green') & 
                         (prev_momentum_color == 'lime'))
        
        exit_long_squeeze = wait_long_exit_by_squeeze & squeeze_back_in
        
        long_exits = exit_long_weak | exit_long_squeeze
        
        # Short exit conditions
        exit_short_weak = (~wait_short_exit_by_squeeze & 
                          (momentum_color == 'maroon') & 
                          (prev_momentum_color == 'red'))
        
        exit_short_squeeze = wait_short_exit_by_squeeze & squeeze_back_in
        
        short_exits = exit_short_weak | exit_short_squeeze
        
        return long_entries, long_exits, short_entries, short_exits
    
    def backtest(self, data: pd.DataFrame, 
                 price_col: str = 'close',
                 high_col: str = 'high',
                 low_col: str = 'low') -> vbt.Portfolio:
        """
        Run backtest on given data
        
        Args:
            data: DataFrame with OHLC data
            price_col: Column name for price data
            high_col: Column name for high data
            low_col: Column name for low data
            
        Returns:
            VectorBT Portfolio object
        """
        # Extract price series
        close = data[price_col]
        high = data[high_col]
        low = data[low_col]
        
        # Calculate indicators
        indicators = self.calculate_indicators(high, low, close)
        
        # Generate signals
        long_entries, long_exits, short_entries, short_exits = self.generate_signals(indicators)
        
        # Create portfolio
        portfolio = vbt.Portfolio.from_signals(
            close=close,
            entries=long_entries,
            exits=long_exits,
            short_entries=short_entries,
            short_exits=short_exits,
            init_cash=self.params['initial_capital'],
            fees=0.001,  # 0.1% fee
            slippage=0.001,  # 0.1% slippage
            freq='1D'  # Daily frequency
        )
        
        # Apply stop loss if enabled
        if self.params['use_stop_loss']:
            # Calculate stop loss levels
            long_stop_loss = close * (1 - self.params['stop_loss_percent'] / 100)
            short_stop_loss = close * (1 + self.params['stop_loss_percent'] / 100)
            
            # Apply stop loss to existing positions
            # This is a simplified implementation - in practice, you'd need
            # to track individual position entry prices
            pass
        
        return portfolio
    
    def optimize_parameters(self, data: pd.DataFrame, 
                           param_ranges: Dict[str, Any],
                           price_col: str = 'close',
                           high_col: str = 'high',
                           low_col: str = 'low') -> pd.DataFrame:
        """
        Optimize strategy parameters
        
        Args:
            data: DataFrame with OHLC data
            param_ranges: Dictionary of parameter ranges to optimize
            price_col: Column name for price data
            high_col: Column name for high data
            low_col: Column name for low data
            
        Returns:
            DataFrame with optimization results
        """
        # Create parameter combinations
        param_combinations = []
        keys = list(param_ranges.keys())
        
        # Generate all parameter combinations
        for values in np.meshgrid(*[param_ranges[key] for key in keys]):
            param_combinations.append(dict(zip(keys, values)))
        
        results = []
        
        for params in param_combinations:
            # Create strategy with current parameters
            strategy = SQZMOMWaveTrendStrategy(**{**self.params, **params})
            
            # Run backtest
            portfolio = strategy.backtest(data, price_col, high_col, low_col)
            
            # Store results
            results.append({
                **params,
                'total_return': portfolio.total_return(),
                'sharpe_ratio': portfolio.sharpe_ratio(),
                'max_drawdown': portfolio.max_drawdown(),
                'win_rate': portfolio.win_rate(),
                'total_trades': len(portfolio.trades())
            })
        
        return pd.DataFrame(results)
    
    def get_kelly_statistics(self, portfolio: vbt.Portfolio) -> Dict[str, float]:
        """
        Calculate Kelly criterion statistics
        
        Args:
            portfolio: VectorBT Portfolio object
            
        Returns:
            Dictionary with Kelly statistics
        """
        # Get trade returns
        trades = portfolio.trades()
        if len(trades) == 0:
            return {
                'mean_return': 0.0,
                'variance_return': 0.0,
                'kelly_fraction': 0.0
            }
        
        # Calculate trade returns as percentages
        trade_returns = trades.pnl / trades.entry_price
        
        # Calculate statistics
        mean_return = trade_returns.mean()
        variance_return = trade_returns.var()
        
        # Kelly fraction
        if variance_return != 0:
            kelly_fraction = mean_return / variance_return
        else:
            kelly_fraction = 0.0
        
        return {
            'mean_return': mean_return,
            'variance_return': variance_return,
            'kelly_fraction': kelly_fraction
        }


# Example usage and testing functions
def create_example_strategy() -> SQZMOMWaveTrendStrategy:
    """Create an example strategy with default parameters"""
    return SQZMOMWaveTrendStrategy(
        bb_length=20,
        bb_mult=2.0,
        kc_length=20,
        kc_mult=1.5,
        use_true_range=True,
        use_confirmed_signal=False,
        wt_channel_length=10,
        wt_avg_length=21,
        trade_direction='both',
        use_stop_loss=False,
        stop_loss_percent=2.0,
        initial_capital=500,
        position_size=0.2
    )


def test_strategy_consistency(data: pd.DataFrame) -> bool:
    """
    Test strategy logic consistency
    
    Args:
        data: Test data
        
    Returns:
        True if consistent, False otherwise
    """
    strategy = create_example_strategy()
    
    try:
        # Calculate indicators
        indicators = strategy.calculate_indicators(data['high'], data['low'], data['close'])
        
        # Generate signals
        signals = strategy.generate_signals(indicators)
        
        # Run backtest
        portfolio = strategy.backtest(data)
        
        # Basic checks
        assert len(indicators) > 0, "No indicators calculated"
        assert len(signals) == 4, "Signal generation failed"
        assert portfolio is not None, "Backtest failed"
        
        return True
        
    except Exception as e:
        print(f"Strategy consistency test failed: {e}")
        return False
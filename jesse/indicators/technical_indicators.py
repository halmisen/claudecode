"""
Technical Indicators for Pine Script Strategy Conversion
Implementing indicators from SQZMOM_WaveTrend_Strategy.PINE
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional

def sma(series: pd.Series, length: int) -> pd.Series:
    """Simple Moving Average"""
    return series.rolling(window=length).mean()

def ema(series: pd.Series, length: int) -> pd.Series:
    """Exponential Moving Average"""
    return series.ewm(span=length, adjust=False).mean()

def stdev(series: pd.Series, length: int) -> pd.Series:
    """Standard Deviation"""
    return series.rolling(window=length).std()

def trange(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    """True Range"""
    high_low = high - low
    high_close = np.abs(high - close.shift(1))
    low_close = np.abs(low - close.shift(1))
    return pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

def highest(series: pd.Series, length: int) -> pd.Series:
    """Highest value over period"""
    return series.rolling(window=length).max()

def lowest(series: pd.Series, length: int) -> pd.Series:
    """Lowest value over period"""
    return series.rolling(window=length).min()

def linreg(series: pd.Series, length: int, offset: int = 0) -> pd.Series:
    """Linear Regression"""
    def linreg_window(x):
        if len(x) < length:
            return np.nan
        y = np.arange(length)
        slope, intercept = np.polyfit(y, x, 1)
        return intercept + slope * (length - 1 + offset)
    
    return series.rolling(window=length).apply(linreg_window, raw=True)

def bollinger_bands(close: pd.Series, length: int = 20, mult: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Bollinger Bands"""
    basis = sma(close, length)
    dev = mult * stdev(close, length)
    upper = basis + dev
    lower = basis - dev
    return basis, upper, lower

def keltner_channels(high: pd.Series, low: pd.Series, close: pd.Series, 
                    length: int = 20, mult: float = 1.5, use_true_range: bool = True) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Keltner Channels"""
    ma = sma(close, length)
    
    if use_true_range:
        rangema = sma(trange(high, low, close), length)
    else:
        rangema = sma(high - low, length)
    
    upper = ma + rangema * mult
    lower = ma - rangema * mult
    return ma, upper, lower

def squeeze_momentum(high: pd.Series, low: pd.Series, close: pd.Series,
                    bb_length: int = 20, bb_mult: float = 2.0,
                    kc_length: int = 20, kc_mult: float = 1.5,
                    use_true_range: bool = True) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    """
    Squeeze Momentum Indicator
    
    Returns:
    - sqz_on: Squeeze is on (BB inside KC)
    - sqz_off: Squeeze is off (BB outside KC)
    - no_sqz: No squeeze condition
    - momentum: Momentum value
    """
    # Bollinger Bands
    bb_basis, bb_upper, bb_lower = bollinger_bands(close, bb_length, bb_mult)
    
    # Keltner Channels
    kc_ma, kc_upper, kc_lower = keltner_channels(high, low, close, kc_length, kc_mult, use_true_range)
    
    # Squeeze conditions
    sqz_on = (bb_lower > kc_lower) & (bb_upper < kc_upper)
    sqz_off = (bb_lower < kc_lower) & (bb_upper > kc_upper)
    no_sqz = ~(sqz_on | sqz_off)
    
    # Momentum calculation
    highest_high = highest(high, kc_length)
    lowest_low = lowest(low, kc_length)
    sma_close = sma(close, kc_length)
    
    momentum_value = linreg(close - ((highest_high + lowest_low) / 2 + sma_close) / 2, kc_length, 0)
    
    return sqz_on, sqz_off, no_sqz, momentum_value

def wavetrend(hlc3: pd.Series, channel_length: int = 10, avg_length: int = 21) -> Tuple[pd.Series, pd.Series]:
    """
    WaveTrend Indicator
    
    Returns:
    - wt1: WaveTrend line 1
    - wt2: WaveTrend line 2 (signal line)
    """
    esa = ema(hlc3, channel_length)
    d = ema(np.abs(hlc3 - esa), channel_length)
    ci = (hlc3 - esa) / (0.015 * d)
    tci = ema(ci, avg_length)
    
    wt1 = tci
    wt2 = sma(wt1, 4)
    
    return wt1, wt2

def get_momentum_color(momentum: pd.Series) -> pd.Series:
    """Get momentum color based on Pine Script logic"""
    colors = pd.Series(index=momentum.index, dtype=object)
    
    # Current and previous momentum values
    current_mom = momentum
    prev_mom = momentum.shift(1)
    
    # Color logic from Pine Script
    colors[(current_mom > 0) & (current_mom > prev_mom)] = 'lime'      # Strong positive
    colors[(current_mom > 0) & (current_mom <= prev_mom)] = 'green'   # Weak positive
    colors[(current_mom <= 0) & (current_mom < prev_mom)] = 'red'      # Strong negative
    colors[(current_mom <= 0) & (current_mom >= prev_mom)] = 'maroon'  # Weak negative
    
    return colors

def safe_divide(numerator: pd.Series, denominator: pd.Series, default_value: float = 0.0) -> pd.Series:
    """Safe division to avoid division by zero"""
    result = numerator / denominator
    result[denominator == 0] = default_value
    return result
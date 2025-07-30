"""
Utility functions for backtesting and data processing
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import requests
import os
from datetime import datetime, timedelta

def prepare_ohlcv_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare OHLCV data for backtesting
    Ensure proper column names and data types
    """
    # Standardize column names
    column_mapping = {
        'open': 'Open',
        'high': 'High', 
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume',
        'timestamp': 'Date',
        'time': 'Date'
    }
    
    # Rename columns if needed
    df = df.rename(columns={col: new_col for col, new_col in column_mapping.items() 
                           if col in df.columns})
    
    # Ensure required columns exist
    required_columns = ['Open', 'High', 'Low', 'Close']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Required column '{col}' not found in data")
    
    # Set Date as index if it exists
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
    
    # Sort by date
    df = df.sort_index()
    
    # Remove duplicates
    df = df[~df.index.duplicated(keep='first')]
    
    return df

def resample_timeframe(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    """
    Resample data to different timeframe
    timeframe: '1H', '2H', '4H', '1D', etc.
    """
    agg_dict = {
        'Open': 'first',
        'High': 'max', 
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }
    
    # Only aggregate columns that exist
    agg_dict = {k: v for k, v in agg_dict.items() if k in df.columns}
    
    # Resample the data (convert to lowercase for pandas compatibility)
    resampled = df.resample(timeframe.lower()).agg(agg_dict).dropna()
    
    # Reset index to make Date a column again
    resampled = resampled.reset_index()
    
    # Ensure the date column is named 'Date' (not 'date' or 'Datetime')
    if 'date' in resampled.columns and 'Date' not in resampled.columns:
        resampled = resampled.rename(columns={'date': 'Date'})
    elif 'Datetime' in resampled.columns and 'Date' not in resampled.columns:
        resampled = resampled.rename(columns={'Datetime': 'Date'})
    
    return resampled

def calculate_kelly_statistics(trades_df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate Kelly criterion statistics from trade results
    """
    if trades_df.empty or len(trades_df) == 0:
        return {
            'mean_return': 0.0,
            'variance_return': 0.0,
            'kelly_fraction': 0.0,
            'win_rate': 0.0,
            'total_trades': 0
        }
    
    # Calculate trade returns as percentage
    trades_df['return_pct'] = (trades_df['pnl'] / trades_df['entry_price']) * 100
    
    # Remove infinite or NaN values
    trades_df = trades_df.replace([np.inf, -np.inf], np.nan).dropna(subset=['return_pct'])
    
    if len(trades_df) == 0:
        return {
            'mean_return': 0.0,
            'variance_return': 0.0,
            'kelly_fraction': 0.0,
            'win_rate': 0.0,
            'total_trades': 0
        }
    
    # Calculate statistics
    mean_return = trades_df['return_pct'].mean()
    variance_return = trades_df['return_pct'].var()
    
    # Kelly fraction calculation
    kelly_fraction = mean_return / variance_return if variance_return != 0 else 0.0
    
    # Win rate
    win_rate = (trades_df['return_pct'] > 0).mean()
    
    return {
        'mean_return': mean_return,
        'variance_return': variance_return,
        'kelly_fraction': kelly_fraction,
        'win_rate': win_rate,
        'total_trades': len(trades_df)
    }

def generate_backtest_report(stats: Dict[str, Any], kelly_stats: Dict[str, float]) -> str:
    """
    Generate a readable backtest report
    """
    report = f"""
=== Backtest Results Summary ===

Basic Statistics:
- Total Return: {stats.get('Return [%]', 0):.2f}%
- Win Rate: {stats.get('Win Rate [%]', 0):.2f}%
- Total Trades: {stats.get('# Trades', 0)}
- Profit Factor: {stats.get('Profit Factor', 0):.2f}
- Max Drawdown: {stats.get('Max. Drawdown [%]', 0):.2f}%
- Sharpe Ratio: {stats.get('Sharpe Ratio', 0):.2f}

Kelly Criterion Statistics:
- Mean Return per Trade: {kelly_stats['mean_return']:.2f}%
- Return Variance: {kelly_stats['variance_return']:.2f}
- Kelly Fraction: {kelly_stats['kelly_fraction']:.2f}
- Win Rate: {kelly_stats['win_rate']:.2%}
- Total Trades: {kelly_stats['total_trades']}

Recommendation:
- Based on Kelly criterion, optimal position size: {max(0, min(kelly_stats['kelly_fraction'], 1.0)):.1%} of capital
"""
    return report

def save_results_to_file(results: Dict[str, Any], filename: str) -> None:
    """
    Save backtest results to file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join('results', f"{filename}_{timestamp}.txt")
    
    # Create results directory if it doesn't exist
    os.makedirs('results', exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"Backtest Results - {timestamp}\n")
        f.write("=" * 50 + "\n\n")
        
        for key, value in results.items():
            if isinstance(value, dict):
                f.write(f"{key}:\n")
                for sub_key, sub_value in value.items():
                    f.write(f"  {sub_key}: {sub_value}\n")
                f.write("\n")
            else:
                f.write(f"{key}: {value}\n")
    
    print(f"Results saved to: {filepath}")

def validate_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate data quality and return quality metrics
    """
    quality_report = {
        'total_rows': len(df),
        'date_range': f"{df.index.min()} to {df.index.max()}",
        'missing_values': df.isnull().sum().to_dict(),
        'duplicate_rows': df.index.duplicated().sum(),
        'zero_volume_days': (df.get('Volume', 0) == 0).sum(),
        'price_gaps': ((df['Close'].diff().abs() / df['Close']) > 0.1).sum()
    }
    
    return quality_report
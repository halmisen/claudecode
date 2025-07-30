"""
Data fetching script for BTC historical data
Uses yfinance for free, reliable data
"""

import pandas as pd
import yfinance as yf
import os
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_utils import prepare_ohlcv_data, resample_timeframe, validate_data_quality

def download_btc_data(start_date: str = "2017-01-01", 
                      end_date: str = None,
                      interval: str = "1d",
                      save_path: str = "data/btc_data.csv") -> pd.DataFrame:
    """
    Download BTC historical data from Yahoo Finance
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format (default: today)
        interval: Data interval (1d, 1h, etc.)
        save_path: Path to save the data
    
    Returns:
        DataFrame with OHLCV data
    """
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"Downloading BTC data from {start_date} to {end_date} with interval {interval}...")
    
    # Download BTC-USD data
    ticker = yf.Ticker("BTC-USD")
    df = ticker.history(start=start_date, end=end_date, interval=interval)
    
    # Reset index to make Date a column
    df = df.reset_index()
    
    # Rename columns to standard format
    df = df.rename(columns={
        'Date': 'Date',
        'Open': 'Open',
        'High': 'High',
        'Low': 'Low',
        'Close': 'Close',
        'Volume': 'Volume'
    })
    
    # Prepare data using our utility function
    df = prepare_ohlcv_data(df)
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # Save to CSV
    df.to_csv(save_path)
    print(f"Data saved to: {save_path}")
    
    # Validate data quality
    quality_report = validate_data_quality(df)
    print("\nData Quality Report:")
    for key, value in quality_report.items():
        print(f"  {key}: {value}")
    
    return df

def load_and_resample_data(csv_path: str, timeframes: list = None) -> dict:
    """
    Load data from CSV and resample to multiple timeframes
    
    Args:
        csv_path: Path to CSV file
        timeframes: List of timeframes to create (e.g., ['1H', '2H', '4H'])
    
    Returns:
        Dictionary with timeframe as key and DataFrame as value
    """
    if timeframes is None:
        timeframes = ['1H', '2H', '4H']
    
    print(f"Loading data from {csv_path}...")
    df = pd.read_csv(csv_path, index_col='Date', parse_dates=True)
    
    timeframe_data = {}
    
    for tf in timeframes:
        print(f"Resampling to {tf} timeframe...")
        resampled_df = resample_timeframe(df, tf)
        timeframe_data[tf] = resampled_df
        
        # Save resampled data
        save_path = csv_path.replace('.csv', f'_{tf}.csv')
        resampled_df.to_csv(save_path)
        print(f"  Saved to: {save_path}")
    
    return timeframe_data

def get_sample_data_for_testing():
    """
    Get sample data for testing purposes (last 6 months)
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    return download_btc_data(
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        save_path="data/btc_sample.csv"
    )

if __name__ == "__main__":
    # Download full dataset (from 2017 to present)
    end_date = datetime.now()
    start_date = datetime(2017, 1, 1)
    
    df = download_btc_data(
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d")
    )
    
    # Create different timeframes
    timeframe_data = load_and_resample_data("data/btc_data.csv", ['1H', '2H', '4H'])
    
    print("\nData preparation complete!")
    print(f"Available timeframes: {list(timeframe_data.keys())}")
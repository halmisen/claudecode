import os
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
import zipfile

def download_single_file(symbol: str, interval: str, year: int, month: int, day: int) -> Optional[List[Dict]]:
    """
    Download a single daily kline file
    """
    base_url = "https://data.binance.vision/data/spot/daily/klines"
    
    # Construct filename
    filename = f"{symbol.upper()}-{interval}-{year:04d}-{month:02d}-{day:02d}.zip"
    url = f"{base_url}/{symbol}/{interval}/{filename}"
    
    try:
        response = requests.get(url, stream=True, timeout=30)
        if response.status_code == 200:
            # Save zip file temporarily
            temp_zip = f"temp_{filename}"
            with open(temp_zip, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Read CSV from zip
            with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                # Get the CSV file inside the zip
                csv_file = zip_ref.namelist()[0]
                with zip_ref.open(csv_file) as csv_file:
                    df = pd.read_csv(csv_file, header=None)
                    data = df.values.tolist()
            
            # Clean up temp file
            os.remove(temp_zip)
            print(f"✓ Downloaded: {filename}")
            return data
        else:
            return None
            
    except Exception as e:
        # Clean up temp file if it exists
        temp_zip = f"temp_{filename}"
        if os.path.exists(temp_zip):
            try:
                os.remove(temp_zip)
            except:
                pass
        return None

def download_binance_klines_parallel(symbol: str, interval: str, start_date: str, end_date: str = None, max_workers: int = 5) -> List[Dict]:
    """
    Download kline data from Binance using parallel downloads
    """
    # Convert date strings to datetime objects
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    else:
        end_dt = datetime.now()
    
    all_data = []
    
    # Generate list of dates to download
    dates = []
    current_dt = start_dt
    while current_dt <= end_dt:
        dates.append((current_dt.year, current_dt.month, current_dt.day))
        current_dt += timedelta(days=1)
    
    print(f"Downloading {len(dates)} files for {symbol.upper()} {interval}...")
    
    # Use ThreadPoolExecutor for parallel downloads
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all download tasks
        future_to_date = {
            executor.submit(download_single_file, symbol, interval, year, month, day): (year, month, day)
            for year, month, day in dates
        }
        
        # Process completed downloads
        for future in as_completed(future_to_date):
            year, month, day = future_to_date[future]
            try:
                data = future.result()
                if data:
                    all_data.extend(data)
            except Exception as e:
                print(f"Error downloading {year}-{month:02d}-{day:02d}: {e}")
    
    return all_data

def save_to_csv(data: List[Dict], filename: str):
    """
    Save data to CSV file
    """
    if not data:
        print("No data to save")
        return
    
    # Define column names for Binance klines
    columns = [
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ]
    
    df = pd.DataFrame(data, columns=columns)
    # Sort by open_time to ensure chronological order
    df = df.sort_values('open_time')
    df.to_csv(filename, index=False)
    print(f"\nData saved to: {filename}")
    print(f"Total records: {len(df)}")

def main():
    # Configuration
    symbol = "btcusdt"
    output_dir = "D:\\BIGBOSS\\claudecode\\backtests\\data"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Download 4-hour data (starting from when 4h data is available)
    print("\n=== Downloading 4-hour data ===")
    # 4h data seems to be available from 2021 onwards
    data_4h = download_binance_klines_parallel(symbol, "4h", "2021-01-01", max_workers=10)
    if data_4h:
        save_to_csv(data_4h, os.path.join(output_dir, f"{symbol}_4h.csv"))
    
    # Download 1-day data
    print("\n=== Downloading 1-day data ===")
    data_1d = download_binance_klines_parallel(symbol, "1d", "2017-08-17", max_workers=10)
    if data_1d:
        save_to_csv(data_1d, os.path.join(output_dir, f"{symbol}_1d.csv"))
    
    print("\nDownload completed!")

if __name__ == "__main__":
    main()
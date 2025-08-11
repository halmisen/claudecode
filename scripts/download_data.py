import argparse
import hashlib
import logging
import os
import sys
import threading
import time
import zipfile
# --- Quickstart Examples ---
#
# This script downloads Binance Futures kline data via command-line arguments.
# You do not need to modify the code to change the symbol or interval.
#
# To download 4-hour data for SOLUSDT:
# python download_data.py --symbol SOLUSDT --interval 4h
#
# To download 1-day data for ETHUSDT and merge it into a single CSV:
# python download_data.py --symbol ETHUSDT --interval 1d --merge-csv
#
# To download COIN-M (inverse perpetuals) data for BTCUSD_PERP:
# python download_data.py --symbol BTCUSD_PERP --interval 1h --market cm
#
# For a full list of options, run:
# python download_data.py --help
#
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Tuple, List
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None


# --- Constants ---
BINANCE_BASE = "https://data.binance.vision"

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
)


# --- Data Structures ---
@dataclass
class DownloadTask:
    url: str
    out_path: str
    checksum_url: str
    description: str  # e.g., "monthly-2023-01" or "daily-2023-02-01"


# --- URL Building ---
def build_kline_zip_url(base_url_template: str, symbol: str, interval: str, date_str: str) -> str:
    return base_url_template.format(
        base=BINANCE_BASE, symbol=symbol, interval=interval, date_str=date_str
    )

def get_url_builders():
    return {
        "monthly": lambda s, i, m, y, mo: f"{BINANCE_BASE}/data/futures/{m}/monthly/klines/{s}/{i}/{s}-{i}-{y}-{mo:02d}.zip",
        "daily": lambda s, i, m, d_str: f"{BINANCE_BASE}/data/futures/{m}/daily/klines/{s}/{i}/{s}-{i}-{d_str}.zip",
    }

# --- Filesystem & Date Utilities ---
def ensure_directory(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def iter_dates(start_date: datetime, end_date: datetime):
    cur = start_date
    while cur <= end_date:
        yield cur
        cur += timedelta(days=1)

def first_day_of_month(d: datetime) -> datetime:
    return datetime(d.year, d.month, 1)

def add_month(d: datetime, months: int) -> datetime:
    year = d.year + (d.month - 1 + months) // 12
    month = (d.month - 1 + months) % 12 + 1
    return datetime(year, month, 1)

def iter_months(start_month_inclusive: datetime, end_month_exclusive: datetime):
    cur = first_day_of_month(start_month_inclusive)
    end = first_day_of_month(end_month_exclusive)
    while cur < end:
        yield cur
        cur = add_month(cur, 1)


# --- Core Download & Verification Logic ---
class RateLimiter:
    def __init__(self, rate_per_sec: float):
        self.enabled = rate_per_sec is not None and rate_per_sec > 0
        self.min_interval = 1.0 / rate_per_sec if self.enabled else 0.0
        self._lock = threading.Lock()
        self._last = 0.0

    def wait(self):
        if not self.enabled:
            return
        with self._lock:
            now = time.monotonic()
            to_wait = self.min_interval - (now - self._last)
            if to_wait > 0:
                time.sleep(to_wait)
            self._last = time.monotonic()

def download_url_to_file(url: str, out_path: str, max_retries: int = 3, timeout: int = 60) -> bool:
    attempt = 0
    while attempt <= max_retries:
        try:
            req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(req, timeout=timeout) as resp:
                if resp.status == 200:
                    tmp_path = out_path + ".part"
                    with open(tmp_path, "wb") as f:
                        while True:
                            chunk = resp.read(1024 * 1024)
                            if not chunk:
                                break
                            f.write(chunk)
                    os.replace(tmp_path, out_path)
                    return True
                else:
                    attempt += 1
                    if attempt > max_retries:
                        logging.error(f"Failed {url}: HTTP {resp.status}")
                        return False
                    time.sleep(1.5 * attempt)
        except HTTPError as e:
            if e.code == 404:
                return False  # Not an error, file just doesn't exist
            attempt += 1
            if attempt > max_retries:
                logging.error(f"Failed {url}: HTTPError {e.code}")
                return False
            time.sleep(1.5 * attempt)
        except URLError as e:
            attempt += 1
            if attempt > max_retries:
                logging.error(f"Failed {url}: URLError {e}")
                return False
            time.sleep(1.5 * attempt)
        except Exception as e:
            attempt += 1
            if attempt > max_retries:
                logging.error(f"Failed {url}: {e}")
                return False
            time.sleep(1.5 * attempt)
    return False

def try_read_text(url: str, timeout: int = 30) -> Optional[str]:
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return resp.read().decode('utf-8', errors='ignore')
            return None
    except Exception:
        return None

def parse_checksum_text(text: str) -> Optional[Tuple[str, str]]:
    if not text: return None
    for line in text.splitlines():
        line = line.strip()
        if not line: continue
        token = line.split()[0]
        hex_str = token.lower()
        if all(c in '0123456789abcdef' for c in hex_str):
            length = len(hex_str)
            if length == 64: return ('sha256', hex_str)
    return None

def compute_file_hash(path: str, algorithm: str) -> Optional[str]:
    try:
        h = hashlib.new(algorithm)
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096 * 1024), b''):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None

def verify_zip_with_checksum(zip_path: str, checksum_url: str) -> bool:
    text = try_read_text(checksum_url)
    if text and (parsed := parse_checksum_text(text)):
        algorithm, expected_hex = parsed
        actual_hex = compute_file_hash(zip_path, algorithm)
        return actual_hex is not None and actual_hex.lower() == expected_hex.lower()

    # Fallback: if checksum fails, test the zip file integrity
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            return zf.testzip() is None
    except Exception:
        return False

def download_worker(task: DownloadTask, rate_limiter: RateLimiter) -> Tuple[str, str]:
    rate_limiter.wait()
    if not download_url_to_file(task.url, task.out_path):
        return task.description, "missing_or_failed"

    if not verify_zip_with_checksum(task.out_path, task.checksum_url):
        logging.warning(f"Checksum verification failed for {task.out_path}. Deleting.")
        try:
            os.remove(task.out_path)
        except OSError as e:
            logging.error(f"Could not delete corrupt file {task.out_path}: {e}")
        return task.description, "failed_checksum"

    return task.description, "downloaded"


# --- Unzip & Merge ---
def unzip_all(zips_dir: str, csv_out_dir: str) -> int:
    ensure_directory(csv_out_dir)
    zip_files = [f for f in sorted(os.listdir(zips_dir)) if f.endswith('.zip')]
    unzipped_count = 0
    
    iterable = tqdm(zip_files, desc="Unzipping files") if tqdm else zip_files
    for name in iterable:
        zip_path = os.path.join(zips_dir, name)
        csv_name = name.replace('.zip', '.csv')
        csv_path = os.path.join(csv_out_dir, csv_name)
        if os.path.exists(csv_path):
            continue
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(csv_out_dir)
                unzipped_count += 1
        except zipfile.BadZipFile:
            logging.warning(f"Corrupt zip (skipping): {zip_path}")
    return unzipped_count

def merge_csv_files(csv_dir: str, output_path: str):
    if not HAS_PANDAS:
        logging.error("Pandas is not installed. Cannot merge CSV files. Please run 'pip install pandas'.")
        return

    all_files = [os.path.join(csv_dir, f) for f in sorted(os.listdir(csv_dir)) if f.endswith('.csv')]
    if not all_files:
        logging.warning(f"No CSV files found in {csv_dir} to merge.")
        return

    logging.info(f"Merging {len(all_files)} CSV files into {os.path.basename(output_path)}...")
    
    # Known Binance columns for futures data
    column_names = [
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ]
    
    df_list = [pd.read_csv(f, header=None, names=column_names) for f in all_files]
    merged_df = pd.concat(df_list, ignore_index=True)
    
    # Filter out any rows that might be headers before converting to numeric
    merged_df = merged_df[pd.to_numeric(merged_df['open_time'], errors='coerce').notna()]

    # Convert timestamp to numeric for sorting if it's not already
    merged_df['open_time'] = pd.to_numeric(merged_df['open_time'])
    
    # Sort by open time and remove duplicates, keeping the first entry
    merged_df.sort_values(by='open_time', inplace=True)
    merged_df.drop_duplicates(subset=['open_time'], keep='first', inplace=True)
    
    merged_df.to_csv(output_path, index=False)
    logging.info(f"Successfully merged and saved to {output_path}")


# --- Main Execution ---
def main():
    parser = argparse.ArgumentParser(
        description=(
            "Download and process Binance Futures kline data. "
            "Downloads historical months as monthly ZIPs and the latest month as daily ZIPs, "
            "then optionally unzips and merges them."
        )
    )
    parser.add_argument('--symbol', default='BTCUSDT', help='Trading pair, e.g., BTCUSDT')
    parser.add_argument('--interval', default='4h', help='Kline interval, e.g., 1m, 1h, 4h, 1d')
    parser.add_argument('--market', default='um', choices=['um', 'cm'], help='Futures market: um (USD-M), cm (COIN-M)')
    parser.add_argument('--start-date', default='2024-01-01', help='Inclusive start date YYYY-MM-DD (default: 2024-01-01)')
    parser.add_argument('--end-date', default=datetime.utcnow().strftime('%Y-%m-%d'), help='Inclusive end date YYYY-MM-DD')
    parser.add_argument('--workers', type=int, default=10, help='Number of concurrent download workers')
    parser.add_argument('--rate-limit', type=float, default=5.0, help='Max requests per second for downloads')
    parser.add_argument('--skip-unzip', action='store_true', help='Only download ZIPs, do not unzip')
    parser.add_argument('--skip-download', action='store_true', help='Only process existing ZIPs, do not download')
    # Merge behavior defaults to ON; allow opting out with --no-merge-csv
    merge_group = parser.add_mutually_exclusive_group()
    merge_group.add_argument('--merge-csv', dest='merge_csv', action='store_true', help='Merge all individual CSVs into a single file after unzipping (default)')
    merge_group.add_argument('--no-merge-csv', dest='merge_csv', action='store_false', help='Do not merge CSVs after unzipping')
    parser.set_defaults(merge_csv=True)

    args = parser.parse_args()

    try:
        start_dt = datetime.strptime(args.start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(args.end_date, '%Y-%m-%d')
    except ValueError:
        logging.error('Invalid --start-date or --end-date. Use YYYY-MM-DD format.')
        sys.exit(2)

    if end_dt < start_dt:
        logging.error('--end-date must be >= --start-date')
        sys.exit(2)

    # Define directory structure (flatten to backtester/data)
    base_dir = os.path.abspath(os.path.join('backtester', 'data', args.symbol, args.interval))
    zips_dir = os.path.join(base_dir, 'zips')
    csv_dir = os.path.join(base_dir, 'csv')
    ensure_directory(zips_dir)
    ensure_directory(csv_dir)

    if not args.skip_download:
        tasks: List[DownloadTask] = []
        url_builders = get_url_builders()

        # --- Prepare Monthly Download Tasks ---
        last_month_first_day = first_day_of_month(end_dt)
        for m in iter_months(first_day_of_month(start_dt), last_month_first_day):
            ym_str = f"{m.year}-{m.month:02d}"
            file_name = f"{args.symbol}-{args.interval}-{ym_str}.zip"
            out_path = os.path.join(zips_dir, file_name)
            if os.path.exists(out_path):
                continue
            
            url = url_builders["monthly"](args.symbol, args.interval, args.market, m.year, m.month)
            tasks.append(DownloadTask(
                url=url,
                out_path=out_path,
                checksum_url=url + ".CHECKSUM",
                description=f"monthly-{ym_str}"
            ))

        # --- Prepare Daily Download Tasks ---
        latest_month_start = max(start_dt, last_month_first_day)
        if latest_month_start <= end_dt:
            for d in iter_dates(latest_month_start, end_dt):
                day_str = d.strftime('%Y-%m-%d')
                file_name = f"{args.symbol}-{args.interval}-{day_str}.zip"
                out_path = os.path.join(zips_dir, file_name)
                if os.path.exists(out_path):
                    continue

                url = url_builders["daily"](args.symbol, args.interval, args.market, day_str)
                tasks.append(DownloadTask(
                    url=url,
                    out_path=out_path,
                    checksum_url=url + ".CHECKSUM",
                    description=f"daily-{day_str}"
                ))
        
        # --- Execute Downloads ---
        if tasks:
            logging.info(f"Found {len(tasks)} new files to download.")
            rate_limiter = RateLimiter(args.rate_limit)
            results = {"downloaded": 0, "missing_or_failed": 0, "failed_checksum": 0}
            
            with ThreadPoolExecutor(max_workers=args.workers) as executor:
                future_to_task = {executor.submit(download_worker, task, rate_limiter): task for task in tasks}
                
                iterable = as_completed(future_to_task)
                if tqdm:
                    iterable = tqdm(iterable, total=len(tasks), desc="Downloading klines")

                for future in iterable:
                    _, status = future.result()
                    results[status] += 1
            
            logging.info(
                f"Download complete. "
                f"Success: {results['downloaded']}, "
                f"Missing/Failed: {results['missing_or_failed']}, "
                f"Checksum Failed: {results['failed_checksum']}"
            )
        else:
            logging.info("All data files already exist. No download needed.")

    if not args.skip_unzip:
        logging.info("Checking for files to unzip...")
        unzipped_count = unzip_all(zips_dir, csv_dir)
        logging.info(f"Unzipped {unzipped_count} new files. CSVs are in: {csv_dir}")

        if args.merge_csv:
            merged_filename = f"{args.symbol}-{args.interval}-merged.csv"
            merged_filepath = os.path.join(base_dir, merged_filename)
            merge_csv_files(csv_dir, merged_filepath)

if __name__ == '__main__':
    main()
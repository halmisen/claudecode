import pandas as pd
from pathlib import Path

def load_data_with_naive_datetime_index(file_path: str | Path) -> pd.DataFrame:
    """
    Loads data from a CSV file, converts the millisecond timestamp column
    into a timezone-naive DatetimeIndex, and returns the processed DataFrame.

    This function does not write any files to disk.

    Args:
        file_path: The path to the CSV file.

    Returns:
        A pandas DataFrame with a naive datetime index, ready for backtesting.
        Returns an empty DataFrame if an error occurs.
    """
    try:
        df = pd.read_csv(file_path)

        # Determine the timestamp column, preferring 'open_time'
        if 'open_time' in df.columns:
            ts_column = 'open_time'
        else:
            # Fallback to the first column if 'open_time' is not present
            ts_column = df.columns[0]

        # Convert millisecond timestamp to a timezone-naive datetime index
        # 1. Convert to datetime object (pandas assumes UTC for unix timestamps)
        # 2. Remove timezone info to make it naive, as required by backtrader
        datetime_index = pd.to_datetime(df.pop(ts_column), unit='ms', utc=True).dt.tz_localize(None)

        df.index = datetime_index
        df.index.name = 'datetime'

        # Ensure standard OHLCV columns are numeric and sort by time
        ohlcv_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in ohlcv_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Sort by index and remove any duplicate timestamps
        df = df.sort_index()
        df = df.loc[~df.index.duplicated(keep='first')]

        return df

    except FileNotFoundError:
        print(f"Error: The file was not found at {file_path}")
        return pd.DataFrame()
    except Exception as e:
        print(f"An error occurred while processing {file_path}: {e}")
        return pd.DataFrame()
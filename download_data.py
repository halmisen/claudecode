import os
import requests
import zipfile
from datetime import datetime
import pandas as pd

def download_and_combine(symbol, interval, dest_path, temp_dir):
    base_url = "https://data.binance.vision/data/spot/monthly/klines"
    
    current_year = datetime.now().year
    all_data = []

    for year in range(2017, current_year + 1):
        for month in range(1, 13):
            file_name = f"{symbol}-{interval}-{year}-{month:02d}.zip"
            url = f"{base_url}/{symbol}/{interval}/{file_name}"
            zip_file_path = os.path.join(temp_dir, file_name)

            try:
                # Download the file
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    with open(zip_file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    # Unzip and read the data
                    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                        csv_file_name = file_name.replace('.zip', '.csv')
                        zip_ref.extract(csv_file_name, temp_dir)
                        df = pd.read_csv(os.path.join(temp_dir, csv_file_name), header=None)
                        all_data.append(df)
                        os.remove(os.path.join(temp_dir, csv_file_name))

                    os.remove(zip_file_path)
                    print(f"Successfully processed data for {year}-{month:02d}")
                elif response.status_code == 404:
                    print(f"No data found for {year}-{month:02d}. Assuming this is the end of the available data.")
                    if year == current_year:
                        break # break from month loop
                else:
                    print(f"Could not download data for {year}-{month:02d}: HTTP Status Code {response.status_code}")

            except requests.exceptions.RequestException as e:
                print(f"Could not download data for {year}-{month:02d}: {e}")
            except Exception as e:
                print(f"An error occurred while processing data for {year}-{month:02d}: {e}")
        else: # continue if inner loop wasn't broken
            continue
        break # break from year loop if inner loop was broken

    if all_data:
        # Concatenate all dataframes
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Save to a single CSV file
        output_filename = f"{symbol}-{interval}-All-Raw.csv"
        combined_df.to_csv(os.path.join(dest_path, output_filename), index=False, header=False)
        print(f"Successfully downloaded and combined raw data for {symbol} {interval} to {output_filename}")
    else:
        print(f"No data downloaded for {symbol} {interval}.")

if __name__ == "__main__":
    data_dir = os.path.join("claudecode", "backtests", "data")
    temp_dir = "D:\\BIGBOSS\\claudecode\\temp_data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # Define the assets and intervals
    symbol = "BTCUSDT"
    intervals = ["4h", "1d"]
    
    for interval in intervals:
        download_and_combine(symbol, interval, data_dir, temp_dir)

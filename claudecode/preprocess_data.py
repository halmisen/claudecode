import pandas as pd
import sys
import os

def preprocess_csv(input_path, output_path):
    try:
        df = pd.read_csv(input_path)
        # Assuming the timestamp is in the first column (index 0)
        # and is in milliseconds
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], unit='ms', errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
        df.to_csv(output_path, index=False)
        print(f"Successfully preprocessed {input_path} to {output_path}")
        return output_path
    except Exception as e:
        print(f"Error preprocessing {input_path}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python preprocess_data.py <input_csv_path> <output_csv_path>", file=sys.stderr)
        sys.exit(1)
    
    input_csv_path = sys.argv[1]
    output_csv_path = sys.argv[2]
    
    preprocess_csv(input_csv_path, output_csv_path)

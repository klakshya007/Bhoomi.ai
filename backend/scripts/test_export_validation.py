import os
import sys
import pandas as pd
import hashlib

def get_file_hash(filepath):
    """Returns SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def main():
    dataset_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'dataset')
    export_1 = os.path.join(dataset_dir, 'observations_1.csv')
    export_2 = os.path.join(dataset_dir, 'observations_2.csv')
    
    # 1. Run export twice
    print("--- 16. Dataset Reproducibility Test ---")
    
    # Add backend/scripts to sys.path to import the exporter
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
    from export_observations import export_observations
    
    print("Running Export #1...")
    export_observations(export_1)
    
    print("Running Export #2...")
    export_observations(export_2)
    
    hash1 = get_file_hash(export_1)
    hash2 = get_file_hash(export_2)
    
    print(f"Export 1 Hash: {hash1}")
    print(f"Export 2 Hash: {hash2}")
    
    if hash1 == hash2:
        print("-> SUCCESS: Datasets are 100% byte-for-byte deterministic.")
    else:
        print("-> FAILED: Datasets differ!")
        
    print("\n--- 15. Validate the Export ---")
    df = pd.read_csv(export_1)
    
    print(f"df.shape: {df.shape}")
    print("\ndf.dtypes:")
    print(df.dtypes)
    print("\ndf.isna().sum():")
    print(df.isna().sum())
    print("\ndf.duplicated().sum():")
    print(df.duplicated().sum())
    
    print("\ndf.head():")
    print(df.head())
    
if __name__ == "__main__":
    main()

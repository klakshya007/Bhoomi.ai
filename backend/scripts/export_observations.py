import os
import sys
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Load .env explicitly since this script runs directly
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.session import engine

def export_observations(output_path: str):
    """Exports the observation table to a CSV file deterministically."""
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Query ordering by ID or observed_at to ensure deterministic output
    query = "SELECT * FROM observation ORDER BY observed_at ASC, id ASC"
    
    df = pd.read_sql(query, engine)
    
    # Export to CSV without the pandas index
    df.to_csv(output_path, index=False)
    return df

if __name__ == "__main__":
    export_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'dataset')
    export_path = os.path.join(export_dir, 'observations.csv')
    
    print(f"Exporting dataset to: {export_path}")
    df = export_observations(export_path)
    print(f"Exported {len(df)} rows.")

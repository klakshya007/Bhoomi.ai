import argparse
import sys
import os
import pandas as pd
from typing import Optional

# Ensure the backend directory is in sys.path so we can import from app
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.db.session import engine
from app.models.domain.observation import Observation
from sqlalchemy.orm import Session

def export_dataset(
    field_id: Optional[str] = None, 
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None,
    output_dir: str = "data"
):
    """
    Exports normalized observations from PostgreSQL to CSV and Parquet.
    This creates the deterministic boundary artifact for Google Colab (Phase 1).
    """
    print("Connecting to database and fetching observations...")
    
    # Construct base query
    query = "SELECT field_id, crop_cycle_id, source, type, depth_interval, value, unit, observed_at, provenance_id FROM observation WHERE 1=1"
    params = {}
    
    if field_id:
        query += " AND field_id = %(field_id)s"
        params['field_id'] = field_id
        
    if start_date:
        query += " AND observed_at >= %(start_date)s"
        params['start_date'] = start_date
        
    if end_date:
        query += " AND observed_at <= %(end_date)s"
        params['end_date'] = end_date
        
    query += " ORDER BY observed_at ASC"
    
    # Execute and read into pandas
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn, params=params)
    except Exception as e:
        print(f"Error querying database: {e}")
        print("Note: Ensure PostgreSQL is running locally and migrations have been applied.")
        sys.exit(1)
        
    if df.empty:
        print("No observations found matching the criteria.")
        sys.exit(0)
        
    print(f"Fetched {len(df)} observations.")
    
    # Ensure output dir exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Save to Parquet (Primary ML Artifact)
    parquet_path = os.path.join(output_dir, "observations_dataset.parquet")
    try:
        df.to_parquet(parquet_path, index=False)
        print(f"Saved primary artifact to {parquet_path}")
    except ImportError:
        print("WARNING: pyarrow or fastparquet not installed. Skipping Parquet export.")
        
    # Save to CSV (Debug/Secondary Artifact)
    csv_path = os.path.join(output_dir, "observations_dataset.csv")
    df.to_csv(csv_path, index=False)
    print(f"Saved secondary artifact to {csv_path}")
    
    print("\nExport completed successfully. This dataset is now ready for Phase 1 (Colab).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export Bhoomi.ai normalized observations to ML-ready datasets.")
    parser.add_argument("--field-id", type=str, help="Filter by a specific Field UUID")
    parser.add_argument("--start-date", type=str, help="Filter by start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, help="Filter by end date (YYYY-MM-DD)")
    parser.add_argument("--out", type=str, default="data", help="Output directory")
    
    args = parser.parse_args()
    
    export_dataset(
        field_id=args.field_id,
        start_date=args.start_date,
        end_date=args.end_date,
        output_dir=args.out
    )

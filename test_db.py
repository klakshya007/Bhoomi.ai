import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from app.db.session import engine
from sqlalchemy import text

def test_db():
    print("Connecting to PostgreSQL...")
    try:
        with engine.connect() as conn:
            # Check PostGIS Version
            version_result = conn.execute(text("SELECT PostGIS_Version();")).fetchone()
            full_version_result = conn.execute(text("SELECT PostGIS_Full_Version();")).fetchone()
            
            print("\nSUCCESS! Connected to PostgreSQL.")
            print(f"PostGIS Version: {version_result[0]}")
            print(f"PostGIS Full Version: {full_version_result[0]}")
            
    except Exception as e:
        print("\nFAILED: Could not connect to PostgreSQL or PostGIS is not installed.")
        print(str(e))

if __name__ == "__main__":
    test_db()

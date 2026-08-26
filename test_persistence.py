import sys
import os
import uuid
from datetime import datetime, timezone

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import text
from app.db.session import SessionLocal
import app.db.base
from app.models.domain.user import User
from app.models.domain.farm import Farm
from app.models.domain.field import Field
from app.models.domain.observation import Observation

def test_persistence():
    db = SessionLocal()
    try:
        print("--- Testing PostGIS Field Geometry ---")
        
        # 1. Setup minimal relational data
        user_id = uuid.uuid4()
        user = User(id=user_id, email=f"test_{user_id}@example.com", name="Test User", hashed_password="fake")
        db.add(user)
        
        farm_id = uuid.uuid4()
        farm = Farm(id=farm_id, user_id=user_id, name="Test Farm")
        db.add(farm)
        
        field_id = uuid.uuid4()
        # WKT string for a simple 1x1 degree square
        wkt_polygon = "SRID=4326;POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))"
        field = Field(id=field_id, farm_id=farm_id, name="Test Field", geometry=wkt_polygon)
        db.add(field)
        
        db.commit()
        print(f"Created Field: {field.id}")

        # 2. Validate PostGIS via Raw SQL
        query = text("""
            SELECT 
                id,
                ST_SRID(geometry) as srid,
                ST_GeometryType(geometry) as type,
                ST_IsValid(geometry) as is_valid
            FROM field
            WHERE id = :fid
        """)
        
        result = db.execute(query, {"fid": field_id}).fetchone()
        print("\nPostGIS Validation Results:")
        print(f"SRID: {result.srid} (Expected: 4326)")
        print(f"Type: {result.type} (Expected: ST_Polygon)")
        print(f"IsValid: {result.is_valid} (Expected: True)")
        
        print("\n--- Testing Observation Persistence ---")
        
        # 3. Create Observation
        obs_id = uuid.uuid4()
        obs = Observation(
            id=obs_id,
            field_id=field_id,
            source="Open-Meteo",
            type="temperature_2m_max",
            value={"raw": 32.5},
            unit="C",
            provenance_id="om_archive_20230101",
            observed_at=datetime(2023, 1, 1, tzinfo=timezone.utc)
        )
        db.add(obs)
        db.commit()
        
        # 4. Fetch and Validate Observation
        fetched_obs = db.query(Observation).filter(Observation.id == obs_id).first()
        print(f"Field ID exists: {fetched_obs.field_id is not None}")
        print(f"Source: {fetched_obs.source}")
        print(f"Type: {fetched_obs.type}")
        print(f"Value: {fetched_obs.value}")
        print(f"Observed At: {fetched_obs.observed_at.isoformat()}")
        print(f"Provenance: {fetched_obs.provenance_id}")
        
    except Exception as e:
        print(f"FAILED: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_persistence()

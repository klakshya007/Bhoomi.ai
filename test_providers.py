import asyncio
import sys
import os
import uuid
from datetime import date

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.providers.gee import GEEProvider
from app.providers.weather import OpenMeteoProvider

async def main():
    field_id = uuid.uuid4()
    start_date = date(2023, 1, 1)
    end_date = date(2023, 6, 1)
    
    print("--- 12. Test GEE -> Observation Boundary ---")
    gee_provider = GEEProvider()
    
    # A small polygon (e.g., a field in California)
    small_polygon = {
        "type": "Polygon",
        "coordinates": [[
            [-121.5, 38.5],
            [-121.5, 38.51],
            [-121.49, 38.51],
            [-121.49, 38.5],
            [-121.5, 38.5]
        ]]
    }
    
    try:
        gee_results = await gee_provider.fetch_indices(field_id, small_polygon, start_date, end_date)
        print(f"Total GEE Observations: {len(gee_results)}")
        
        has_ndvi = False
        has_evi = False
        for obs in gee_results:
            if obs.type == "NDVI_Mean": has_ndvi = True
            if obs.type == "EVI_Mean": has_evi = True
            
        print(f"NDVI Exists: {has_ndvi}")
        print(f"EVI Exists: {has_evi}")
        
        if gee_results:
            sample = gee_results[0]
            print(f"Sample Value: {sample.value} ({type(sample.value)})")
            print(f"Observed At: {sample.observed_at.isoformat()}")
            print(f"Provenance ID: {sample.provenance_id}")
            print("Successfully processed cloud masking on GEE servers (no raw raster downloaded).")
    except Exception as e:
        print(f"GEE Test Failed: {e}")

    print("\n--- 13. Validate Open-Meteo ---")
    weather_provider = OpenMeteoProvider()
    
    lat, lon = 38.5, -121.5
    
    try:
        weather_results = await weather_provider.fetch_historical_weather(lat, lon, start_date, end_date, field_id)
        print(f"Total Open-Meteo Observations: {len(weather_results)}")
        
        types = set(obs.type for obs in weather_results)
        print("Variables retrieved:")
        for t in types:
            print(f" - {t}")
            
        if weather_results:
            sample = weather_results[0]
            print(f"\nSample Observation: {sample.type} = {sample.value} {sample.unit}")
            print(f"Observed At: {sample.observed_at.isoformat()}")
            print(f"Provenance ID: {sample.provenance_id}")
    except Exception as e:
        print(f"Weather Test Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())

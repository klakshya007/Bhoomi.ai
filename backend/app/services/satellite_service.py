from typing import Dict, Any

class SatelliteService:
    async def get_satellite_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch and aggregate satellite remote sensing data for coordinates."""
        return {
            "latitude": lat,
            "longitude": lon,
            "ndvi": 0.68,
            "evi": 0.45
        }

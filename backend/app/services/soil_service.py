from typing import Dict, Any

class SoilService:
    async def get_soil_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch and aggregate soil quality metrics for coordinates."""
        return {
            "latitude": lat,
            "longitude": lon,
            "ph": 6.5,
            "nitrogen": 140.0,
            "phosphorus": 30.0,
            "potassium": 200.0,
            "moisture": 22.5
        }

from typing import Dict, Any

class WeatherService:
    async def get_weather_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch and aggregate weather metrics for coordinates."""
        return {
            "latitude": lat,
            "longitude": lon,
            "temperature": 28.5,
            "humidity": 65.0,
            "rainfall": 12.0
        }

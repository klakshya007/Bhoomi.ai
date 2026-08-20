"""
Weather tool functions.
"""

def fetch_forecast(lat: float, lon: float) -> dict:
    """Tool function for retrieving weather forecast data."""
    return {"status": "success", "forecast": "Sunny", "latitude": lat, "longitude": lon}

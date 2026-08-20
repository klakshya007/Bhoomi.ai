"""
Satellite integration tool functions.
"""

def fetch_sentinel_imagery(lat: float, lon: float) -> dict:
    """Tool function for retrieving Sentinel satellite imagery."""
    return {"status": "success", "ndvi": 0.68, "latitude": lat, "longitude": lon}

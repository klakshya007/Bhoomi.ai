"""
Simulation tool functions.
"""

def run_yield_simulation(crop: str, weather_scenario: str) -> dict:
    """Tool function for simulating crop yield under scenarios."""
    return {"crop": crop, "scenario": weather_scenario, "expected_yield_ton_per_ha": 4.2}

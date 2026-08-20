from typing import Dict, Any

class ExplainabilityAgent:
    """Agent providing explainable reasoning for AI insights and recommendations."""

    async def explain(self, model_outputs: dict) -> Dict[str, Any]:
        """Generate human-readable explanation for model prediction outputs."""
        return {
            "explanation": "Low stress due to adequate rainfall and high NDVI values."
        }

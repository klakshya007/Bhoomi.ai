from typing import Dict, Any
from uuid import UUID
import logging

from app.services.soil_service import SoilService
from app.providers.soil import SoilGridsWCSProvider

logger = logging.getLogger(__name__)

async def get_soil_profile(field_id: UUID, latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Agent-ready deterministic tool to retrieve the soil profile for a location.
    Catches exceptions safely and returns a dictionary.
    """
    try:
        provider = SoilGridsWCSProvider()
        service = SoilService(provider=provider)
        
        dtos = await service.get_soil_profile_for_field(
            field_id=field_id,
            latitude=latitude,
            longitude=longitude
        )
        
        return {
            "success": True,
            "data": [dto.model_dump(mode="json") for dto in dtos]
        }
    except ValueError as e:
        logger.warning(f"Validation error in get_soil_profile: {e}")
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        logger.error(f"Unexpected error in get_soil_profile: {e}")
        return {
            "success": False,
            "error": "Failed to fetch soil profile due to an internal error."
        }

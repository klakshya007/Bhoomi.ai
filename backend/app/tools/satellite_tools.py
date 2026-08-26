from uuid import UUID
from datetime import date
from app.services.satellite_service import SatelliteService
from app.core.exceptions import IntegrationError

async def fetch_satellite_indices_tool(field_id: str, geojson_polygon: dict, start_date: str, end_date: str) -> dict:
    """
    Agent-facing tool for fetching historical Sentinel-2 NDVI/EVI data.
    Deterministic execution, catches integration errors to prevent agent crash.
    """
    try:
        service = SatelliteService()
        parsed_uuid = UUID(field_id)
        parsed_start = date.fromisoformat(start_date)
        parsed_end = date.fromisoformat(end_date)
        
        # Execute the service
        observations = await service.get_historical_indices(
            field_id=parsed_uuid, 
            geojson_polygon=geojson_polygon,
            start_date=parsed_start,
            end_date=parsed_end
        )
        
        # Return simple dict format for the Agent
        return {
            "success": True,
            "count": len(observations),
            "data": [obs.model_dump(mode='json') for obs in observations]
        }
    except ValueError as e:
        return {"success": False, "error": f"Validation error: {str(e)}"}
    except IntegrationError as e:
        return {"success": False, "error": f"Provider error: {e.message}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected tool failure: {str(e)}"}

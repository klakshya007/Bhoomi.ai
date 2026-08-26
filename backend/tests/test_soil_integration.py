import pytest
import uuid
import httpx
from datetime import datetime, timezone
from typing import List

from app.providers.soil import SoilGridsWCSProvider, SoilPropertyResult
from app.services.soil_service import SoilService
from app.tools.soil_tools import get_soil_profile
from app.models.schemas import NormalizedObservationDTO

# Pytest mark for async tests
pytestmark = pytest.mark.anyio

class MockSoilGridsWCSProvider(SoilGridsWCSProvider):
    async def get_soil_properties(self, latitude: float, longitude: float) -> List[SoilPropertyResult]:
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            raise ValueError("Invalid coordinates")
            
        # Simulate network error if latitude is exactly 0.0 for testing error propagation
        if latitude == 0.0:
            raise RuntimeError("WCS request failed: simulated network error")
            
        return [
            SoilPropertyResult(
                property_name="phh2o",
                depth_interval="0-5cm",
                mean_value=6.5,
                uncertainty=0.2,
                unit="pH"
            ),
            SoilPropertyResult(
                property_name="soc",
                depth_interval="0-5cm",
                mean_value=25.0,
                uncertainty=None, # Testing None uncertainty
                unit="dg/kg"
            )
        ]

async def test_provider_boundary_success():
    provider = MockSoilGridsWCSProvider()
    results = await provider.get_soil_properties(45.0, 90.0)
    
    assert len(results) == 2
    assert results[0].property_name == "phh2o"
    assert results[0].depth_interval == "0-5cm"
    assert results[0].uncertainty == 0.2
    
async def test_provider_invalid_coordinates():
    provider = MockSoilGridsWCSProvider()
    with pytest.raises(ValueError, match="Invalid coordinates"):
        await provider.get_soil_properties(95.0, 0.0)

async def test_service_normalization():
    provider = MockSoilGridsWCSProvider()
    service = SoilService(provider)
    field_id = uuid.uuid4()
    
    dtos = await service.get_soil_profile_for_field(field_id, 45.0, 90.0)
    
    assert len(dtos) == 2
    assert isinstance(dtos[0], NormalizedObservationDTO)
    assert dtos[0].field_id == field_id
    assert dtos[0].source == "ISRIC_SoilGrids"
    assert dtos[0].type == "soil_phh2o"
    assert dtos[0].depth_interval == "0-5cm"
    assert dtos[0].value == 6.5
    assert dtos[0].metadata == {"uncertainty": 0.2}
    
    assert dtos[1].type == "soil_soc"
    assert dtos[1].metadata is None

async def test_tool_boundary_success(monkeypatch):
    # Monkeypatch the provider inside the tool
    monkeypatch.setattr("app.tools.soil_tools.SoilGridsWCSProvider", MockSoilGridsWCSProvider)
    
    field_id = uuid.uuid4()
    result = await get_soil_profile(field_id, 45.0, 90.0)
    
    assert result["success"] is True
    assert len(result["data"]) == 2
    assert result["data"][0]["type"] == "soil_phh2o"

async def test_tool_boundary_validation_error(monkeypatch):
    monkeypatch.setattr("app.tools.soil_tools.SoilGridsWCSProvider", MockSoilGridsWCSProvider)
    
    field_id = uuid.uuid4()
    result = await get_soil_profile(field_id, 95.0, 0.0)
    
    assert result["success"] is False
    assert "Invalid coordinates" in result["error"]

async def test_tool_boundary_network_error(monkeypatch):
    monkeypatch.setattr("app.tools.soil_tools.SoilGridsWCSProvider", MockSoilGridsWCSProvider)
    
    field_id = uuid.uuid4()
    # MockSoilGridsWCSProvider raises RuntimeError when lat=0.0
    result = await get_soil_profile(field_id, 0.0, 0.0)
    
    assert result["success"] is False
    assert "internal error" in result["error"]

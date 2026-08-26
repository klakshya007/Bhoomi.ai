import pytest
import asyncio
from unittest.mock import patch, MagicMock
from datetime import date, datetime, timezone
from uuid import uuid4
from app.providers.gee import GEEProvider
from app.services.satellite_service import SatelliteService
from app.tools.satellite_tools import fetch_satellite_indices_tool
from app.core.exceptions import IntegrationError

# --- FIXTURES & MOCKS ---
TEST_POLYGON = {
    "type": "Polygon",
    "coordinates": [[[77.5, 12.9], [77.6, 12.9], [77.6, 13.0], [77.5, 13.0], [77.5, 12.9]]]
}
INVALID_POLYGON = {"type": "Point", "coordinates": [77.5, 12.9]} # Should fail ee.Geometry.Polygon

# Mock a successful return from GEE `.getInfo()`
MOCK_FC_INFO = {
    'type': 'FeatureCollection',
    'features': [
        {
            'type': 'Feature',
            'properties': {
                'system:time_start': 1672531200000,  # 2023-01-01
                'system:index': '20230101_T43P',
                'NDVI': 0.65,
                'EVI': 0.45
            }
        },
        {
            'type': 'Feature',
            'properties': {
                'system:time_start': 1673395200000,  # 2023-01-11
                'system:index': '20230111_T43P',
                'NDVI': 0.68,
                'EVI': 0.48
            }
        }
    ]
}

MOCK_FC_EMPTY = {
    'type': 'FeatureCollection',
    'features': []
}


# --- TESTS ---

@pytest.fixture
def mock_ee():
    with patch('app.providers.gee.ee') as mock_ee_lib:
        mock_ee_lib.Initialize.return_value = None
        mock_ee_lib.ServiceAccountCredentials.return_value = None
        
        # Setup mock geometry behavior
        def mock_polygon(coords):
            if not isinstance(coords, list) or len(coords) == 0 or len(coords[0]) == 0 or not isinstance(coords[0][0], list):
                 raise Exception("Invalid geometry")
            return MagicMock()
            
        mock_ee_lib.Geometry.Polygon.side_effect = mock_polygon
        
        # Ensure SCL mask constants exist
        mock_ee_lib.Filter.lt.return_value = MagicMock()
        mock_ee_lib.Reducer.mean.return_value = MagicMock()
        
        yield mock_ee_lib


@pytest.mark.anyio
@patch('app.providers.gee.asyncio.to_thread')
async def test_valid_ndvi_evi_calculation(mock_to_thread, mock_ee):
    # Mock the thread blocking call returning the FeatureCollection dict
    mock_to_thread.return_value = MOCK_FC_INFO
    
    provider = GEEProvider()
    field_id = uuid4()
    
    observations = await provider.fetch_indices(
        field_id=field_id,
        geojson_polygon=TEST_POLYGON,
        start_date=date(2023, 1, 1),
        end_date=date(2023, 1, 31)
    )
    
    # 2 dates * 2 indices (NDVI, EVI) = 4 observations
    assert len(observations) == 4
    
    # Verify first NDVI
    ndvi_obs = next(obs for obs in observations if obs.type == "NDVI_Mean" and obs.value == 0.65)
    assert ndvi_obs.field_id == field_id
    assert ndvi_obs.source == "GEE_Sentinel2"
    assert ndvi_obs.unit == "index"
    assert ndvi_obs.observed_at == datetime.fromtimestamp(1672531200, tz=timezone.utc)
    assert ndvi_obs.provenance_id == "COPERNICUS/S2_SR_HARMONIZED_20230101_T43P"


@pytest.mark.anyio
@patch('app.providers.gee.asyncio.to_thread')
async def test_empty_collection(mock_to_thread, mock_ee):
    # E.g. purely cloudy period, no images survived the mask
    mock_to_thread.return_value = MOCK_FC_EMPTY
    
    provider = GEEProvider()
    observations = await provider.fetch_indices(
        field_id=uuid4(),
        geojson_polygon=TEST_POLYGON,
        start_date=date(2023, 1, 1),
        end_date=date(2023, 1, 31)
    )
    
    assert len(observations) == 0


@pytest.mark.anyio
async def test_invalid_polygon(mock_ee):
    provider = GEEProvider()
    
    with pytest.raises(IntegrationError, match="Invalid GeoJSON polygon"):
        await provider.fetch_indices(
            field_id=uuid4(),
            geojson_polygon=INVALID_POLYGON,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 31)
        )


@pytest.mark.anyio
@patch('app.providers.gee.asyncio.to_thread')
async def test_gee_exception_propagation(mock_to_thread, mock_ee):
    # Simulate Earth Engine API crash (e.g. rate limit) during the blocking call
    mock_to_thread.side_effect = Exception("Earth Engine capacity exceeded")
    
    provider = GEEProvider()
    with pytest.raises(IntegrationError, match="GEE computation failed"):
        await provider.fetch_indices(
            field_id=uuid4(),
            geojson_polygon=TEST_POLYGON,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 31)
        )


# --- TOOL & SERVICE BOUNDARY ---

@pytest.mark.anyio
@patch('app.providers.gee.asyncio.to_thread')
async def test_tool_boundary_success(mock_to_thread, mock_ee):
    mock_to_thread.return_value = MOCK_FC_INFO
    
    result = await fetch_satellite_indices_tool(
        field_id=str(uuid4()),
        geojson_polygon=TEST_POLYGON,
        start_date="2023-01-01",
        end_date="2023-01-31"
    )
    
    assert result["success"] is True
    assert result["count"] == 4
    assert len(result["data"]) == 4


@pytest.mark.anyio
@patch('app.providers.gee.asyncio.to_thread')
async def test_tool_boundary_error_propagation(mock_to_thread, mock_ee):
    # Test that the tool catches an IntegrationError gracefully
    mock_to_thread.side_effect = Exception("Simulated EE Error")
    
    result = await fetch_satellite_indices_tool(
        field_id=str(uuid4()),
        geojson_polygon=TEST_POLYGON,
        start_date="2023-01-01",
        end_date="2023-01-31"
    )
    
    assert result["success"] is False
    assert "Provider error" in result["error"]

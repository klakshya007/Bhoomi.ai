import pytest
import httpx
from datetime import date, timezone
from uuid import uuid4
from app.providers.weather import OpenMeteoProvider
from app.services.weather_service import WeatherService
from app.tools.weather_tools import fetch_historical_weather_tool
from app.core.exceptions import IntegrationError

# --- MOCK DATA ---
VALID_RESPONSE = {
    "daily_units": {
        "time": "iso8601",
        "temperature_2m_mean": "°C",
        "relative_humidity_2m_mean": "%",
        "precipitation_sum": "mm",
        "wind_speed_10m_max": "km/h",
        "et0_fao_evapotranspiration": "mm"
    },
    "daily": {
        "time": ["2023-01-01", "2023-01-02"],
        "temperature_2m_mean": [20.5, 21.0],
        "relative_humidity_2m_mean": [60.0, 62.5],
        "precipitation_sum": [0.0, 5.2],
        "wind_speed_10m_max": [12.0, 15.5],
        "et0_fao_evapotranspiration": [3.5, 3.2]
    }
}

MISSING_VAR_RESPONSE = {
    "daily": {
        "time": ["2023-01-01"],
        "temperature_2m_mean": [20.5]
        # Missing precipitation, wind, etc.
    }
}

LENGTH_MISMATCH_RESPONSE = {
    "daily": {
        "time": ["2023-01-01", "2023-01-02"],
        "temperature_2m_mean": [20.5, 21.0],
        "relative_humidity_2m_mean": [60.0, 62.5],
        "precipitation_sum": [0.0], # Mismatch!
        "wind_speed_10m_max": [12.0, 15.5],
        "et0_fao_evapotranspiration": [3.5, 3.2]
    }
}

NULL_VALUE_RESPONSE = {
    "daily_units": {"temperature_2m_mean": "°C", "relative_humidity_2m_mean": "%", "precipitation_sum": "mm", "wind_speed_10m_max": "km/h", "et0_fao_evapotranspiration": "mm"},
    "daily": {
        "time": ["2023-01-01"],
        "temperature_2m_mean": [None], # Simulating missing data for a day
        "relative_humidity_2m_mean": [60.0],
        "precipitation_sum": [0.0],
        "wind_speed_10m_max": [12.0],
        "et0_fao_evapotranspiration": [3.5]
    }
}

# --- HANDLERS ---
def mock_valid_handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=VALID_RESPONSE)

def mock_missing_var_handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=MISSING_VAR_RESPONSE)

def mock_mismatch_handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=LENGTH_MISMATCH_RESPONSE)

def mock_null_handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=NULL_VALUE_RESPONSE)

def mock_http_error_handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(500, text="Internal Server Error")

def mock_timeout_handler(request: httpx.Request) -> httpx.Response:
    raise httpx.TimeoutException("Mocked timeout")


# --- TESTS ---

@pytest.mark.anyio
async def test_valid_response_normalization():
    field_id = uuid4()
    transport = httpx.MockTransport(mock_valid_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        provider = OpenMeteoProvider(client=client)
        
        observations = await provider.fetch_historical_weather(
            lat=12.9, lon=77.5, start_date=date(2023, 1, 1), end_date=date(2023, 1, 2), field_id=field_id
        )
        
        # 5 variables * 2 days = 10 observations
        assert len(observations) == 10
        
        # Verify first temperature observation
        temp_obs = next(obs for obs in observations if obs.type == "temperature_2m_mean")
        assert temp_obs.field_id == field_id
        assert temp_obs.value == 20.5
        assert temp_obs.unit == "°C"
        assert temp_obs.source == "OpenMeteo"
        assert temp_obs.observed_at.tzinfo == timezone.utc

@pytest.mark.anyio
async def test_invalid_coordinates():
    provider = OpenMeteoProvider()
    with pytest.raises(IntegrationError, match="latitude"):
        await provider.fetch_historical_weather(lat=95.0, lon=77.5, start_date=date(2023,1,1), end_date=date(2023,1,2), field_id=uuid4())
    
    with pytest.raises(IntegrationError, match="longitude"):
        await provider.fetch_historical_weather(lat=12.0, lon=200.0, start_date=date(2023,1,1), end_date=date(2023,1,2), field_id=uuid4())

@pytest.mark.anyio
async def test_invalid_date_range():
    provider = OpenMeteoProvider()
    with pytest.raises(IntegrationError, match="start_date must be less than"):
        # start date is after end date
        await provider.fetch_historical_weather(lat=12.0, lon=77.5, start_date=date(2023,1,2), end_date=date(2023,1,1), field_id=uuid4())

@pytest.mark.anyio
async def test_http_failure():
    transport = httpx.MockTransport(mock_http_error_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        provider = OpenMeteoProvider(client=client)
        with pytest.raises(IntegrationError, match="HTTP Error"):
            await provider.fetch_historical_weather(lat=12.9, lon=77.5, start_date=date(2023, 1, 1), end_date=date(2023, 1, 2), field_id=uuid4())

@pytest.mark.anyio
async def test_timeout_failure():
    transport = httpx.MockTransport(mock_timeout_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        provider = OpenMeteoProvider(client=client)
        with pytest.raises(IntegrationError, match="timed out"):
            await provider.fetch_historical_weather(lat=12.9, lon=77.5, start_date=date(2023, 1, 1), end_date=date(2023, 1, 2), field_id=uuid4())

@pytest.mark.anyio
async def test_missing_requested_variable():
    transport = httpx.MockTransport(mock_missing_var_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        provider = OpenMeteoProvider(client=client)
        with pytest.raises(IntegrationError, match="Missing requested variable"):
            await provider.fetch_historical_weather(lat=12.9, lon=77.5, start_date=date(2023, 1, 1), end_date=date(2023, 1, 1), field_id=uuid4())

@pytest.mark.anyio
async def test_time_value_array_mismatch():
    transport = httpx.MockTransport(mock_mismatch_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        provider = OpenMeteoProvider(client=client)
        with pytest.raises(IntegrationError, match="Array length mismatch"):
            await provider.fetch_historical_weather(lat=12.9, lon=77.5, start_date=date(2023, 1, 1), end_date=date(2023, 1, 2), field_id=uuid4())

@pytest.mark.anyio
async def test_null_value_handling():
    transport = httpx.MockTransport(mock_null_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        provider = OpenMeteoProvider(client=client)
        observations = await provider.fetch_historical_weather(lat=12.9, lon=77.5, start_date=date(2023, 1, 1), end_date=date(2023, 1, 1), field_id=uuid4())
        
        # 5 variables requested, but temp is None, so only 4 observations should be created
        assert len(observations) == 4
        # Verify temperature is not in the results
        assert not any(obs.type == "temperature_2m_mean" for obs in observations)

# --- SERVICE & TOOL BOUNDARY TESTS ---

@pytest.mark.anyio
async def test_service_provider_boundary():
    # Inject mocked provider into service
    transport = httpx.MockTransport(mock_valid_handler)
    client = httpx.AsyncClient(transport=transport)
    provider = OpenMeteoProvider(client=client)
    service = WeatherService(provider=provider)
    
    observations = await service.get_historical_weather(uuid4(), 12.0, 77.0, date(2023,1,1), date(2023,1,2))
    assert len(observations) == 10

@pytest.mark.anyio
async def test_tool_service_error_propagation(monkeypatch):
    # Test that the tool catches an IntegrationError gracefully
    async def mock_service_fail(*args, **kwargs):
        raise IntegrationError("Simulated DB or Provider Error")
        
    monkeypatch.setattr(WeatherService, "get_historical_weather", mock_service_fail)
    
    res = await fetch_historical_weather_tool(
        field_id=str(uuid4()), lat=12.0, lon=77.0, start_date="2023-01-01", end_date="2023-01-02"
    )
    
    assert res["success"] is False
    assert "Provider error" in res["error"]

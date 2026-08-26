import asyncio
import json
import ee
from typing import List, Optional
from datetime import date, datetime, timezone
from uuid import UUID

from app.config.settings import settings
from app.core.exceptions import IntegrationError, ProviderDataFormatError
from app.models.schemas import NormalizedObservationDTO


class GEEProvider:
    """
    Provider for Earth Engine and Sentinel-2 data.
    Authentication is lazy and .getInfo() operations run in threads.
    """
    
    _initialized = False

    def __init__(self):
        self.collection_id = "COPERNICUS/S2_SR_HARMONIZED"

    def _initialize(self):
        """Lazy authentication and initialization of the Earth Engine SDK."""
        if GEEProvider._initialized:
            return
            
        try:
            if settings.GEE_SERVICE_ACCOUNT_JSON:
                # Use service account credentials if provided in env
                credentials = ee.ServiceAccountCredentials(
                    "", key_file=settings.GEE_SERVICE_ACCOUNT_JSON
                )
                ee.Initialize(credentials, project=settings.GEE_PROJECT_ID)
            else:
                # Fallback to local default credentials for development
                # Requires running `earthengine authenticate` locally first
                ee.Initialize()
                
            GEEProvider._initialized = True
        except Exception as e:
            raise IntegrationError(f"Earth Engine authentication failed: {str(e)}", provider="GEE")

    def _mask_clouds(self, image: ee.Image) -> ee.Image:
        """
        Mask clouds and shadows using the Scene Classification (SCL) band.
        SCL Values: 3 (Cloud shadows), 8 (Cloud medium prob), 
                    9 (Cloud high prob), 10 (Thin cirrus)
        """
        scl = image.select('SCL')
        mask = scl.neq(3).And(scl.neq(8)).And(scl.neq(9)).And(scl.neq(10))
        return image.updateMask(mask)

    def _add_indices(self, image: ee.Image) -> ee.Image:
        """
        Calculates NDVI and EVI using Sentinel-2 bands.
        Scaling factors (Bands are scaled by 10000) are localized here.
        """
        # Sentinel-2 bands
        nir = image.select('B8')
        red = image.select('B4')
        blue = image.select('B2')

        # NDVI = (NIR - Red) / (NIR + Red)
        ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')

        # EVI = 2.5 * ((NIR - Red) / (NIR + 6 * Red - 7.5 * Blue + 10000))
        # Note: B8, B4, B2 are scaled by 10000. So the constant 1 needs to be scaled as 10000.
        evi = image.expression(
            '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 10000))', {
                'NIR': nir,
                'RED': red,
                'BLUE': blue
            }).rename('EVI')

        return image.addBands([ndvi, evi])

    async def fetch_indices(
        self, field_id: UUID, geojson_polygon: dict, start_date: date, end_date: date
    ) -> List[NormalizedObservationDTO]:
        """
        Retrieves cloud-masked NDVI and EVI indices over a time period for a polygon.
        """
        self._initialize()

        try:
            # Create EE Geometry from GeoJSON
            roi = ee.Geometry.Polygon(geojson_polygon["coordinates"])
        except Exception as e:
            raise IntegrationError(f"Invalid GeoJSON polygon: {str(e)}", provider="GEE")

        def _compute():
            # Sentinel-2 SR collection
            collection = (
                ee.ImageCollection(self.collection_id)
                .filterBounds(roi)
                .filterDate(start_date.isoformat(), end_date.isoformat())
                .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 30))
                .map(self._mask_clouds)
                .map(self._add_indices)
            )

            # Define reduction function per image
            def _reduce_image(image):
                # Reduce over the Region of Interest (ROI)
                reduced = image.reduceRegion(
                    reducer=ee.Reducer.mean(),
                    geometry=roi,
                    scale=10,
                    maxPixels=1e9
                )
                
                # We need the image timestamp and granule ID for provenance
                return ee.Feature(None, {
                    'system:time_start': image.get('system:time_start'),
                    'system:index': image.get('system:index'),
                    'NDVI': reduced.get('NDVI'),
                    'EVI': reduced.get('EVI')
                })

            # Map the reduction over the collection and return a FeatureCollection
            reduced_collection = collection.map(_reduce_image)
            
            # Blocking network call isolated in this function
            return reduced_collection.getInfo()

        try:
            # Execute the blocking GEE network call in a thread pool
            feature_collection = await asyncio.to_thread(_compute)
        except Exception as e:
            raise IntegrationError(f"GEE computation failed: {str(e)}", provider="GEE")

        return self._normalize_response(feature_collection, field_id)

    def _normalize_response(self, fc_info: dict, field_id: UUID) -> List[NormalizedObservationDTO]:
        """Maps the GEE FeatureCollection dictionary into Normalized DTOs."""
        if 'features' not in fc_info:
            raise ProviderDataFormatError("GEE response missing 'features' array", provider="GEE")

        observations = []
        for feature in fc_info['features']:
            props = feature.get('properties', {})
            
            time_start_ms = props.get('system:time_start')
            granule_id = props.get('system:index')
            ndvi = props.get('NDVI')
            evi = props.get('EVI')

            if time_start_ms is None or granule_id is None:
                continue

            # Convert JS timestamp ms to UTC datetime
            dt = datetime.fromtimestamp(time_start_ms / 1000.0, tz=timezone.utc)
            provenance = f"{self.collection_id}_{granule_id}"

            if ndvi is not None:
                observations.append(
                    NormalizedObservationDTO(
                        field_id=field_id,
                        source="GEE_Sentinel2",
                        type="NDVI_Mean",
                        value=float(ndvi),
                        unit="index",
                        observed_at=dt,
                        provenance_id=provenance
                    )
                )

            if evi is not None:
                observations.append(
                    NormalizedObservationDTO(
                        field_id=field_id,
                        source="GEE_Sentinel2",
                        type="EVI_Mean",
                        value=float(evi),
                        unit="index",
                        observed_at=dt,
                        provenance_id=provenance
                    )
                )

        return observations

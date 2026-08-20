from fastapi import APIRouter, Depends
from app.models.schemas import AdvisoryRequest, AdvisoryResponse
from app.api.dependencies import get_advisory_service
from app.services.advisory_service import AdvisoryService

router = APIRouter(prefix="/advisory", tags=["Advisory"])

@router.post("", response_model=AdvisoryResponse)
async def get_advisory(
    request: AdvisoryRequest,
    service: AdvisoryService = Depends(get_advisory_service)
):
    data = await service.generate_advisory(request.latitude, request.longitude, request.crop_type)
    return AdvisoryResponse(**data)

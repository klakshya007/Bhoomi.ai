from fastapi import APIRouter
from app.models.schemas import PredictionRequest, PredictionResponse

router = APIRouter(prefix="/prediction", tags=["Prediction"])

@router.post("", response_model=PredictionResponse)
async def predict_crop_stress(request: PredictionRequest):
    return PredictionResponse(
        crop_stress_index=0.15,
        risk_level="Low",
        details={"latitude": request.latitude, "longitude": request.longitude}
    )

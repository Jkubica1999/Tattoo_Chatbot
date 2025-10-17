from fastapi import APIRouter
from pydantic import BaseModel
from app.core.estimator import estimate

router = APIRouter()

class EstReq(BaseModel):
    size_band: str
    style: str
    placement: str
    color: str
    rate: float | None = None
    shop_min: float | None = None

@router.post("/estimate")
def estimate_endpoint(req: EstReq):
    hours, low, high = estimate(
        req.size_band, req.style, req.placement, req.color,
        rate=req.rate or 120.0, shop_min=req.shop_min or 80.0
    )
    return {"hours": hours, "price_low": low, "price_high": high}

"""Exposure / risk analysis endpoints."""
from __future__ import annotations
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.prediction import ExposureResult

logger = logging.getLogger("landsense.api.exposure")
router = APIRouter()


@router.get("/{area_id}", response_model=ExposureResult)
def exposure_analysis(area_id: int, db: Session = Depends(get_db)):
    """Basic exposure analysis — identify elements near high-susceptibility zones.

    In demo mode, returns synthetic exposure indicators derived from
    the prediction grid. In production, this would use road/settlement
    vector layers with spatial queries.
    """
    from app.models import Prediction
    preds = (
        db.query(Prediction)
        .filter(Prediction.study_area_id == area_id)
        .all()
    )

    if not preds:
        return ExposureResult(study_area_id=area_id)

    total = len(preds)
    high = sum(
        1 for p in preds
        if p.susceptibility_class in ("High", "Very High")
    )
    high_pct = round(high / total * 100, 1) if total else 0

    # Simplified exposure counts based on demo proximity data
    # In production, this would run spatial intersection queries
    nearby_roads = min(high, 5)
    nearby_settlements = min(high // 3, 3)

    return ExposureResult(
        study_area_id=area_id,
        high_susceptibility_pct=high_pct,
        nearby_roads=nearby_roads,
        nearby_settlements=nearby_settlements,
        details=[
            {"type": "road", "count": nearby_roads,
             "note": "Roads intersecting or near high-susceptibility zones"},
            {"type": "settlement", "count": nearby_settlements,
             "note": "Settlements near high-susceptibility zones"},
        ],
    )


@router.get("/nearby-lower")
def nearby_lower_susceptibility(
    lat: float = Query(...),
    lng: float = Query(...),
    study_area_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """Find nearby locations with lower model-estimated susceptibility.

    IMPORTANT: These are NOT 'guaranteed safe' locations.
    They are areas with lower model-estimated susceptibility only.
    """
    from app.models import Prediction
    import math

    preds = (
        db.query(Prediction)
        .filter(Prediction.study_area_id == study_area_id)
        .all()
    )

    if not preds:
        raise HTTPException(404, "No predictions found for this area")

    # Find lower-susceptibility points within ~5km radius
    results = []
    for p in preds:
        if p.susceptibility_class in ("Very Low", "Low"):
            dlat = p.latitude - lat
            dlng = p.longitude - lng
            dist_km = math.sqrt(dlat**2 + dlng**2) * 111  # approx
            if dist_km <= 5.0:
                results.append({
                    "latitude": p.latitude,
                    "longitude": p.longitude,
                    "probability": p.probability,
                    "susceptibility_class": p.susceptibility_class,
                    "distance_km": round(dist_km, 2),
                })

    results.sort(key=lambda x: x["distance_km"])

    return {
        "query_lat": lat,
        "query_lng": lng,
        "nearby_lower_susceptibility": results[:10],
        "note": (
            "These are lower-susceptibility areas based on model estimates only. "
            "They are NOT guaranteed safe locations. "
            "Always follow official emergency guidance."
        ),
    }

"""Prediction endpoints — location and area-wide grid prediction."""
from __future__ import annotations
import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ModelResult, Prediction, TrainingRun
from app.schemas.prediction import (
    LocationPredictRequest,
    LocationPredictResponse,
    AreaPredictRequest,
    AreaPredictResponse,
    GridPredictionPoint,
    PredictionHistoryOut,
)

logger = logging.getLogger("landsense.api.predictions")
router = APIRouter()


def _classify(prob: float) -> str:
    """Map probability to susceptibility class."""
    from app.config import settings
    if prob < settings.thresh_very_low:
        return "Very Low"
    elif prob < settings.thresh_low:
        return "Low"
    elif prob < settings.thresh_moderate:
        return "Moderate"
    elif prob < settings.thresh_high:
        return "High"
    return "Very High"


@router.post("/location", response_model=LocationPredictResponse)
def predict_location(body: LocationPredictRequest, db: Session = Depends(get_db)):
    """Predict landslide susceptibility for a single lat/lng."""
    from app.ml.predictor import predict_single_location

    # Find the model to use
    if body.model_result_id:
        model = db.query(ModelResult).filter(
            ModelResult.id == body.model_result_id
        ).first()
    else:
        # Use the best model from the latest completed run for this study area
        run = (
            db.query(TrainingRun)
            .filter(
                TrainingRun.study_area_id == body.study_area_id,
                TrainingRun.status == "completed",
            )
            .order_by(TrainingRun.run_date.desc())
            .first()
        )
        if not run or not run.best_model_id:
            raise HTTPException(
                404,
                "No trained model found. Train a model first.",
            )
        model = db.query(ModelResult).filter(
            ModelResult.id == run.best_model_id
        ).first()

    if not model:
        raise HTTPException(404, "Model not found")

    result = predict_single_location(
        model_result=model,
        latitude=body.latitude,
        longitude=body.longitude,
    )

    # Save prediction
    pred = Prediction(
        study_area_id=body.study_area_id,
        model_result_id=model.id,
        latitude=body.latitude,
        longitude=body.longitude,
        probability=result["probability"],
        susceptibility_class=result["susceptibility_class"],
        features_at_location=json.dumps(result.get("features", {})),
        top_factors=json.dumps(result.get("important_factors", [])),
    )
    db.add(pred)
    db.commit()

    return LocationPredictResponse(
        latitude=body.latitude,
        longitude=body.longitude,
        probability=result["probability"],
        susceptibility_class=result["susceptibility_class"],
        features=result.get("features", {}),
        important_factors=result.get("important_factors", []),
        model_name=model.model_name or "",
    )


@router.post("/area", response_model=AreaPredictResponse)
def predict_area(body: AreaPredictRequest, db: Session = Depends(get_db)):
    """Generate grid predictions for the entire study area."""
    from app.ml.predictor import predict_area_grid

    # Find model
    if body.model_result_id:
        model = db.query(ModelResult).filter(
            ModelResult.id == body.model_result_id
        ).first()
    else:
        run = (
            db.query(TrainingRun)
            .filter(
                TrainingRun.study_area_id == body.study_area_id,
                TrainingRun.status == "completed",
            )
            .order_by(TrainingRun.run_date.desc())
            .first()
        )
        if not run or not run.best_model_id:
            raise HTTPException(404, "No trained model found.")
        model = db.query(ModelResult).filter(
            ModelResult.id == run.best_model_id
        ).first()

    if not model:
        raise HTTPException(404, "Model not found")

    from app.models import StudyArea
    area = db.query(StudyArea).filter(
        StudyArea.id == body.study_area_id
    ).first()
    if not area:
        raise HTTPException(404, "Study area not found")

    grid_result = predict_area_grid(
        model_result=model,
        bbox=(area.bbox_minlat, area.bbox_minlng,
              area.bbox_maxlat, area.bbox_maxlng),
        resolution=body.grid_resolution,
    )

    return AreaPredictResponse(
        study_area_id=body.study_area_id,
        model_name=model.model_name or "",
        grid_resolution=body.grid_resolution,
        n_points=len(grid_result["predictions"]),
        predictions=[
            GridPredictionPoint(**p) for p in grid_result["predictions"]
        ],
        class_distribution=grid_result.get("class_distribution", {}),
    )


@router.get("/", response_model=list[PredictionHistoryOut])
def list_predictions(db: Session = Depends(get_db)):
    """List recent predictions."""
    return (
        db.query(Prediction)
        .order_by(Prediction.created_at.desc())
        .limit(100)
        .all()
    )

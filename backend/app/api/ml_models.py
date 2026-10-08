"""Model listing, comparison, and detail endpoints."""
from __future__ import annotations
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ModelResult, TrainingRun
from app.schemas.training import ModelResultOut, ModelComparisonOut

logger = logging.getLogger("landsense.api.models")
router = APIRouter()


@router.get("/", response_model=list[ModelResultOut])
def list_models(db: Session = Depends(get_db)):
    """List all trained model results."""
    return (
        db.query(ModelResult)
        .order_by(ModelResult.roc_auc.desc())
        .all()
    )


@router.get("/{model_id}", response_model=ModelResultOut)
def get_model(model_id: int, db: Session = Depends(get_db)):
    """Return details for a single model result."""
    m = db.query(ModelResult).filter(ModelResult.id == model_id).first()
    if not m:
        raise HTTPException(404, "Model not found")
    return m


@router.get("/compare/{run_id}")
def compare_models(run_id: str, db: Session = Depends(get_db)):
    """Compare all models from a single training run side-by-side."""
    tr = db.query(TrainingRun).filter(TrainingRun.run_id == run_id).first()
    if not tr:
        raise HTTPException(404, f"Training run '{run_id}' not found")

    results = (
        db.query(ModelResult)
        .filter(ModelResult.training_run_id == tr.id)
        .order_by(ModelResult.roc_auc.desc())
        .all()
    )

    best = next((m for m in results if m.is_best), results[0] if results else None)

    return {
        "run_id": run_id,
        "study_area_id": tr.study_area_id,
        "best_model": best.model_name if best else None,
        "models": [
            {
                "id": m.id,
                "model_name": m.model_name,
                "accuracy": m.accuracy,
                "precision_score": m.precision_score,
                "recall": m.recall,
                "f1_score": m.f1_score,
                "roc_auc": m.roc_auc,
                "roc_auc_std": m.roc_auc_std,
                "training_time_s": m.training_time_s,
                "confusion_matrix": m.confusion_matrix,
                "feature_importance": m.feature_importance,
                "is_best": m.is_best,
            }
            for m in results
        ],
    }

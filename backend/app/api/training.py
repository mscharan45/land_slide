"""Training dataset creation and model training endpoints."""
from __future__ import annotations
import json
import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import (
    TrainingDataset, TrainingRun, ModelResult,
    HistoricalLandslide, Feature,
)
from app.schemas.training import (
    TrainingDatasetCreate, TrainingDatasetOut,
    TrainRequest, TrainingRunOut,
)

logger = logging.getLogger("landsense.api.training")
router = APIRouter()


@router.post("/dataset", response_model=TrainingDatasetOut, status_code=201)
def create_training_dataset(
    body: TrainingDatasetCreate, db: Session = Depends(get_db)
):
    """Build an ML-ready training dataset from available GIS data.

    For demo mode: uses the synthetic demo CSV directly.
    For real mode: extracts feature values from raster/vector layers
    at landslide and non-landslide sample locations.
    """
    import pandas as pd

    # Check for demo dataset
    demo_csv = settings.demo_dir / "demo_training_data.csv"
    if demo_csv.exists():
        df = pd.read_csv(demo_csv)
        features_used = [
            c for c in df.columns
            if c not in ("latitude", "longitude", "label", "id")
        ]
        n_pos = int((df["label"] == 1).sum())
        n_neg = int((df["label"] == 0).sum())

        version = f"DEMO_V{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        td = TrainingDataset(
            study_area_id=body.study_area_id,
            version=version,
            file_path=str(demo_csv),
            n_samples=len(df),
            n_features=len(features_used),
            n_positive=n_pos,
            n_negative=n_neg,
            features_used=json.dumps(features_used),
            is_synthetic=True,
        )
        db.add(td)
        db.commit()
        db.refresh(td)
        logger.info("Created training dataset id=%s (demo)", td.id)
        return td

    # Real mode — placeholder for GIS-based extraction
    raise HTTPException(
        501,
        "Real GIS-based training dataset creation will be implemented in Phase 2. "
        "Generate the demo dataset first via POST /api/demo/generate.",
    )


@router.get("/runs", response_model=list[TrainingRunOut])
def list_training_runs(db: Session = Depends(get_db)):
    """List all training runs."""
    return db.query(TrainingRun).order_by(TrainingRun.run_date.desc()).all()


@router.get("/runs/{run_id}")
def get_training_run(run_id: str, db: Session = Depends(get_db)):
    """Get a training run by its run_id, including model results."""
    tr = db.query(TrainingRun).filter(TrainingRun.run_id == run_id).first()
    if not tr:
        raise HTTPException(404, f"Training run '{run_id}' not found")

    results = (
        db.query(ModelResult)
        .filter(ModelResult.training_run_id == tr.id)
        .order_by(ModelResult.roc_auc.desc())
        .all()
    )

    return {
        "run": {
            "id": tr.id,
            "run_id": tr.run_id,
            "study_area_id": tr.study_area_id,
            "status": tr.status,
            "cv_folds": tr.cv_folds,
            "random_seed": tr.random_seed,
            "n_features": tr.n_features,
            "n_samples": tr.n_samples,
            "balancing_method": tr.balancing_method,
            "features_used": tr.features_used,
            "run_date": str(tr.run_date) if tr.run_date else None,
            "best_model_id": tr.best_model_id,
        },
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


@router.post("/train")
def train_models(body: TrainRequest, db: Session = Depends(get_db)):
    """Train multiple ML models and compare their performance.

    This endpoint runs the full ML pipeline:
    1. Load the training dataset
    2. Preprocess (scale, encode, handle missing)
    3. Train each requested model with stratified k-fold CV
    4. Evaluate all models
    5. Select the best model by ROC-AUC
    6. Save models and metadata
    """
    from app.ml.trainer import run_training_pipeline

    # Validate the training dataset exists
    td = db.query(TrainingDataset).filter(
        TrainingDataset.id == body.training_dataset_id
    ).first()
    if not td:
        raise HTTPException(404, "Training dataset not found")

    run_id = f"RUN_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

    # Create the training run record
    tr = TrainingRun(
        study_area_id=body.study_area_id,
        training_dataset_id=body.training_dataset_id,
        run_id=run_id,
        cv_folds=body.cv_folds,
        random_seed=body.random_seed,
        balancing_method=body.balancing_method,
        status="running",
    )
    db.add(tr)
    db.commit()
    db.refresh(tr)

    try:
        results = run_training_pipeline(
            training_run_id=tr.id,
            dataset_path=td.file_path,
            model_names=body.models,
            cv_folds=body.cv_folds,
            random_seed=body.random_seed,
            balancing_method=body.balancing_method,
            selected_features=body.selected_features,
            db=db,
        )

        tr.status = "completed"
        tr.n_features = results.get("n_features", 0)
        tr.n_samples = results.get("n_samples", 0)
        tr.features_used = json.dumps(results.get("features_used", []))
        tr.best_model_id = results.get("best_model_id")
        db.commit()

        logger.info("Training run %s completed. Best model id=%s",
                     run_id, tr.best_model_id)

        return {
            "run_id": run_id,
            "status": "completed",
            "best_model": results.get("best_model_name"),
            "best_roc_auc": results.get("best_roc_auc"),
            "n_models": results.get("n_models"),
        }

    except Exception as exc:
        tr.status = "failed"
        tr.notes = str(exc)[:500]
        db.commit()
        logger.error("Training run %s failed: %s", run_id, exc, exc_info=True)
        raise HTTPException(500, f"Training failed: {exc}")

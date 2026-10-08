"""Feature registry endpoints — list, toggle, availability check."""
from __future__ import annotations
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Feature, Dataset
from app.schemas.feature import (
    FeatureAvailability,
    FeatureAvailabilityReport,
    FeatureOut,
    FeatureToggle,
)

logger = logging.getLogger("landsense.api.features")
router = APIRouter()


@router.get("/", response_model=list[FeatureOut])
def list_features(db: Session = Depends(get_db)):
    """Return all features in the registry."""
    return db.query(Feature).order_by(Feature.category, Feature.name).all()


@router.put("/{feature_id}", response_model=FeatureOut)
def toggle_feature(
    feature_id: int, body: FeatureToggle, db: Session = Depends(get_db)
):
    """Enable or disable a feature."""
    feat = db.query(Feature).filter(Feature.id == feature_id).first()
    if not feat:
        raise HTTPException(404, "Feature not found")
    feat.is_enabled = body.is_enabled
    db.commit()
    db.refresh(feat)
    return feat


@router.get("/availability/{area_id}", response_model=FeatureAvailabilityReport)
def feature_availability(area_id: int, db: Session = Depends(get_db)):
    """Check which features have data available for a study area."""
    features = db.query(Feature).order_by(Feature.category).all()

    # Datasets linked to this study area, keyed by feature_name
    datasets = (
        db.query(Dataset)
        .filter(Dataset.study_area_id == area_id)
        .all()
    )
    available_names = {ds.feature_name for ds in datasets if ds.feature_name}

    items: list[FeatureAvailability] = []
    available_count = 0
    missing_count = 0

    for f in features:
        if f.name in available_names:
            status = "Available"
            available_count += 1
            # Find the matching dataset for quality info
            ds = next((d for d in datasets if d.feature_name == f.name), None)
            quality = ds.quality_score if ds else None
            miss = ds.missing_pct if ds else None
        else:
            if f.is_required:
                status = "Missing"
            else:
                status = "Optional"
            missing_count += 1
            quality = None
            miss = None

        items.append(
            FeatureAvailability(
                name=f.name,
                display_name=f.display_name,
                category=f.category,
                status=status,
                quality_score=quality,
                missing_pct=miss,
                is_enabled=f.is_enabled,
            )
        )

    return FeatureAvailabilityReport(
        study_area_id=area_id,
        total_candidate=len(features),
        available=available_count,
        missing=missing_count,
        features=items,
    )

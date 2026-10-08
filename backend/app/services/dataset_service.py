"""
LandSense AI — Dataset Service.
"""
from __future__ import annotations
import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.models import Dataset


class DatasetService:
    @staticmethod
    def get_by_study_area(db: Session, study_area_id: int):
        return db.query(Dataset).filter(Dataset.study_area_id == study_area_id).all()

    @staticmethod
    def get_quality_summary(db: Session, study_area_id: int):
        datasets = DatasetService.get_by_study_area(db, study_area_id)
        return {
            "total_layers": len(datasets),
            "rasters": len([d for d in datasets if d.dataset_type == "raster"]),
            "vectors": len([d for d in datasets if d.dataset_type == "vector"]),
            "average_coverage": (
                round(sum(d.spatial_coverage_pct or 0 for d in datasets) / max(len(datasets), 1), 1)
            ),
        }

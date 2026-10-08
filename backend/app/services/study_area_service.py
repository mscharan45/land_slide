"""
LandSense AI — Study Area Service.
"""
from __future__ import annotations
import json
from sqlalchemy.orm import Session
from app.models import StudyArea
from app.schemas.study_area import StudyAreaCreate


class StudyAreaService:
    @staticmethod
    def get_all(db: Session):
        return db.query(StudyArea).order_by(StudyArea.created_at.desc()).all()

    @staticmethod
    def get_by_id(db: Session, area_id: int):
        return db.query(StudyArea).filter(StudyArea.id == area_id).first()

    @staticmethod
    def create(db: Session, data: StudyAreaCreate):
        boundary_json = json.dumps(data.boundary) if data.boundary else None
        area = StudyArea(
            name=data.name,
            description=data.description,
            boundary=boundary_json,
            bbox_minlat=data.bbox_minlat,
            bbox_minlng=data.bbox_minlng,
            bbox_maxlat=data.bbox_maxlat,
            bbox_maxlng=data.bbox_maxlng,
            area_sqkm=data.area_sqkm,
        )
        db.add(area)
        db.commit()
        db.refresh(area)
        return area

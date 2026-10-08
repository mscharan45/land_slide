"""Study Area CRUD endpoints."""
from __future__ import annotations
import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import StudyArea
from app.schemas.study_area import StudyAreaCreate, StudyAreaOut, StudyAreaSummary

logger = logging.getLogger("landsense.api.study_areas")
router = APIRouter()


@router.get("/", response_model=list[StudyAreaSummary])
def list_study_areas(db: Session = Depends(get_db)):
    """Return all study areas."""
    return db.query(StudyArea).order_by(StudyArea.created_at.desc()).all()


@router.post("/", response_model=StudyAreaOut, status_code=201)
def create_study_area(payload: StudyAreaCreate, db: Session = Depends(get_db)):
    """Create a new study area."""
    boundary_str: Optional[str] = None
    if payload.boundary is not None:
        boundary_str = json.dumps(payload.boundary)

    area = StudyArea(
        name=payload.name,
        description=payload.description,
        boundary=boundary_str,
        bbox_minlat=payload.bbox_minlat,
        bbox_minlng=payload.bbox_minlng,
        bbox_maxlat=payload.bbox_maxlat,
        bbox_maxlng=payload.bbox_maxlng,
        area_sqkm=payload.area_sqkm,
    )
    db.add(area)
    db.commit()
    db.refresh(area)
    logger.info("Created study area id=%s name=%s", area.id, area.name)
    return area


@router.get("/{area_id}", response_model=StudyAreaOut)
def get_study_area(area_id: int, db: Session = Depends(get_db)):
    """Return a single study area by ID."""
    area = db.query(StudyArea).filter(StudyArea.id == area_id).first()
    if not area:
        raise HTTPException(404, f"Study area {area_id} not found")
    return area


@router.delete("/{area_id}", status_code=204)
def delete_study_area(area_id: int, db: Session = Depends(get_db)):
    """Delete a study area."""
    area = db.query(StudyArea).filter(StudyArea.id == area_id).first()
    if not area:
        raise HTTPException(404, f"Study area {area_id} not found")
    db.delete(area)
    db.commit()
    return None

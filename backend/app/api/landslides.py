"""Historical landslide inventory endpoints."""
from __future__ import annotations
import csv
import io
import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import HistoricalLandslide
from app.schemas.study_area import StudyAreaOut   # reuse for type hints

logger = logging.getLogger("landsense.api.landslides")
router = APIRouter()


class LandslideOut:
    """Simple dict-serializable landslide record."""
    pass


@router.get("/")
def list_landslides(
    study_area_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    """List historical landslide records, optionally filtered."""
    q = db.query(HistoricalLandslide)
    if study_area_id is not None:
        q = q.filter(HistoricalLandslide.study_area_id == study_area_id)
    rows = q.order_by(HistoricalLandslide.id).all()
    return [
        {
            "id": r.id,
            "study_area_id": r.study_area_id,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "event_date": r.event_date,
            "source": r.source,
            "confidence": r.confidence,
            "notes": r.notes,
        }
        for r in rows
    ]


@router.get("/stats/{area_id}")
def landslide_stats(area_id: int, db: Session = Depends(get_db)):
    """Return summary statistics for landslides in a study area."""
    q = db.query(HistoricalLandslide).filter(
        HistoricalLandslide.study_area_id == area_id
    )
    total = q.count()
    records = q.all()

    by_source: dict[str, int] = {}
    by_year: dict[str, int] = {}
    for r in records:
        src = r.source or "Unknown"
        by_source[src] = by_source.get(src, 0) + 1
        if r.event_date:
            year = r.event_date[:4]
            by_year[year] = by_year.get(year, 0) + 1

    return {
        "study_area_id": area_id,
        "total": total,
        "by_source": by_source,
        "by_year": dict(sorted(by_year.items())),
    }


@router.post("/upload")
async def upload_landslides(
    file: UploadFile = File(...),
    study_area_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """Upload a CSV of historical landslide locations.

    Expected columns: latitude, longitude, [event_date], [source], [confidence], [notes]
    """
    contents = await file.read()
    text = contents.decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(text))

    required = {"latitude", "longitude"}
    if not required.issubset(set(reader.fieldnames or [])):
        raise HTTPException(
            400,
            f"CSV must contain columns: {required}. "
            f"Found: {reader.fieldnames}",
        )

    count = 0
    for row in reader:
        try:
            lat = float(row["latitude"])
            lng = float(row["longitude"])
        except (ValueError, KeyError):
            continue

        record = HistoricalLandslide(
            study_area_id=study_area_id,
            latitude=lat,
            longitude=lng,
            event_date=row.get("event_date") or row.get("date"),
            source=row.get("source", "CSV Upload"),
            confidence=row.get("confidence", "unknown"),
            notes=row.get("notes"),
        )
        db.add(record)
        count += 1

    db.commit()
    logger.info("Uploaded %d landslide records for area %s", count, study_area_id)
    return {"uploaded": count, "study_area_id": study_area_id}

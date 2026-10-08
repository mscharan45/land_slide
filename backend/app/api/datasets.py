"""Dataset upload, listing, and validation endpoints."""
from __future__ import annotations
import logging
import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Dataset
from app.schemas.dataset import DatasetOut, DatasetUploadOut, DatasetValidationResult

logger = logging.getLogger("landsense.api.datasets")
router = APIRouter()

ALLOWED_EXTENSIONS = {".tif", ".tiff", ".geojson", ".json", ".csv", ".shp", ".zip"}
MAX_SIZE_BYTES = settings.max_upload_size_mb * 1024 * 1024


@router.get("/", response_model=list[DatasetOut])
def list_datasets(
    study_area_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    """List datasets, optionally filtered by study area."""
    q = db.query(Dataset)
    if study_area_id is not None:
        q = q.filter(Dataset.study_area_id == study_area_id)
    return q.order_by(Dataset.created_at.desc()).all()


@router.get("/{dataset_id}", response_model=DatasetOut)
def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Return a single dataset's metadata."""
    ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not ds:
        raise HTTPException(404, "Dataset not found")
    return ds


@router.post("/upload", response_model=DatasetUploadOut, status_code=201)
async def upload_dataset(
    file: UploadFile = File(...),
    study_area_id: int = Query(...),
    feature_name: str = Query(""),
    db: Session = Depends(get_db),
):
    """Upload a GeoTIFF / GeoJSON / CSV file."""
    # ── Validate extension ───────────────────────────────────────────────
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            400,
            f"Unsupported file type '{ext}'. Allowed: {ALLOWED_EXTENSIONS}",
        )

    # ── Validate size ────────────────────────────────────────────────────
    contents = await file.read()
    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(
            413,
            f"File exceeds {settings.max_upload_size_mb} MB limit",
        )

    # ── Sanitize filename & save ─────────────────────────────────────────
    safe_name = f"{uuid.uuid4().hex}_{os.path.basename(file.filename or 'file')}"
    save_path = settings.upload_dir / safe_name
    with open(save_path, "wb") as f:
        f.write(contents)

    # ── Determine type ───────────────────────────────────────────────────
    if ext in {".tif", ".tiff"}:
        dtype = "raster"
    elif ext in {".geojson", ".json", ".shp", ".zip"}:
        dtype = "vector"
    else:
        dtype = "csv"

    ds = Dataset(
        study_area_id=study_area_id,
        name=file.filename or safe_name,
        dataset_type=dtype,
        feature_name=feature_name or None,
        file_path=str(save_path),
        status="uploaded",
    )
    db.add(ds)
    db.commit()
    db.refresh(ds)
    logger.info("Uploaded dataset id=%s name=%s", ds.id, ds.name)
    return ds


@router.post("/validate", response_model=DatasetValidationResult)
def validate_dataset(dataset_id: int = Query(...), db: Session = Depends(get_db)):
    """Run basic validation checks on an uploaded dataset."""
    ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not ds:
        raise HTTPException(404, "Dataset not found")

    warnings: list[str] = []
    errors: list[str] = []

    if not os.path.exists(ds.file_path or ""):
        errors.append("File not found on disk")
        return DatasetValidationResult(
            valid=False, file_type=ds.dataset_type or "unknown", errors=errors
        )

    # Basic validation — real GIS validation happens in the GIS module
    crs = None
    resolution = None
    bounds = None
    n_bands = None

    if ds.dataset_type == "raster":
        try:
            import rasterio
            with rasterio.open(ds.file_path) as src:
                crs = str(src.crs)
                resolution = abs(src.res[0])
                bounds = {
                    "left": src.bounds.left,
                    "bottom": src.bounds.bottom,
                    "right": src.bounds.right,
                    "top": src.bounds.top,
                }
                n_bands = src.count
                if src.crs is None:
                    warnings.append("Raster has no CRS defined")
        except Exception as exc:
            errors.append(f"Cannot read raster: {exc}")
    elif ds.dataset_type == "csv":
        try:
            import pandas as pd
            df = pd.read_csv(ds.file_path, nrows=5)
            if df.empty:
                warnings.append("CSV file is empty")
        except Exception as exc:
            errors.append(f"Cannot read CSV: {exc}")

    valid = len(errors) == 0
    if valid:
        ds.status = "validated"
        ds.crs = crs
        ds.resolution_m = resolution
        db.commit()

    return DatasetValidationResult(
        valid=valid,
        file_type=ds.dataset_type or "unknown",
        crs=crs,
        resolution_m=resolution,
        bounds=bounds,
        n_bands=n_bands,
        warnings=warnings,
        errors=errors,
    )

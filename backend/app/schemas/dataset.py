"""Pydantic schemas for Dataset endpoints."""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DatasetUploadOut(BaseModel):
    """Response after a file is uploaded."""
    id: int
    name: str
    dataset_type: str
    feature_name: Optional[str] = None
    file_path: str
    crs: Optional[str] = None
    status: str
    is_synthetic: bool = False
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class DatasetOut(BaseModel):
    """Full dataset detail."""
    id: int
    study_area_id: Optional[int] = None
    name: str
    dataset_type: Optional[str] = None
    feature_name: Optional[str] = None
    file_path: Optional[str] = None
    crs: Optional[str] = None
    resolution_m: Optional[float] = None
    spatial_coverage_pct: Optional[float] = None
    missing_pct: Optional[float] = None
    quality_score: Optional[str] = None
    source: Optional[str] = None
    license: Optional[str] = None
    temporal_period: Optional[str] = None
    download_date: Optional[str] = None
    is_synthetic: bool = False
    status: str = "uploaded"
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class DatasetValidationResult(BaseModel):
    """Result of validating an uploaded dataset file."""
    valid: bool
    file_type: str
    crs: Optional[str] = None
    resolution_m: Optional[float] = None
    bounds: Optional[dict] = None
    n_bands: Optional[int] = None
    n_features: Optional[int] = None
    missing_pct: Optional[float] = None
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class DatasetSummaryStats(BaseModel):
    """Summary statistics for the dataset explorer."""
    n_rows: int
    n_columns: int
    columns: list[dict]
    sample_rows: list[dict]
    class_distribution: Optional[dict] = None

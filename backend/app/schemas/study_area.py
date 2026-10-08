"""Pydantic schemas for Study Area endpoints."""
from __future__ import annotations
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class StudyAreaCreate(BaseModel):
    """Payload to create a new study area."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    boundary: Optional[dict[str, Any]] = Field(
        None, description="GeoJSON Polygon / MultiPolygon geometry"
    )
    bbox_minlat: Optional[float] = Field(None, ge=-90, le=90)
    bbox_minlng: Optional[float] = Field(None, ge=-180, le=180)
    bbox_maxlat: Optional[float] = Field(None, ge=-90, le=90)
    bbox_maxlng: Optional[float] = Field(None, ge=-180, le=180)
    area_sqkm: Optional[float] = None


class StudyAreaOut(BaseModel):
    """Serialized study area returned by the API."""
    id: int
    name: str
    description: Optional[str] = None
    boundary: Optional[str] = None
    bbox_minlat: Optional[float] = None
    bbox_minlng: Optional[float] = None
    bbox_maxlat: Optional[float] = None
    bbox_maxlng: Optional[float] = None
    area_sqkm: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class StudyAreaSummary(BaseModel):
    """Lightweight summary used in list responses."""
    id: int
    name: str
    area_sqkm: Optional[float] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

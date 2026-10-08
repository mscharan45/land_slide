"""Pydantic schemas for Feature registry endpoints."""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


class FeatureOut(BaseModel):
    """Single feature definition from the registry."""
    id: int
    name: str
    display_name: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    data_type: Optional[str] = None
    source_type: Optional[str] = None
    is_required: bool = False
    is_enabled: bool = True
    preprocessing: Optional[str] = None
    extraction_method: Optional[str] = None
    description: Optional[str] = None
    tooltip: Optional[str] = None

    model_config = {"from_attributes": True}


class FeatureToggle(BaseModel):
    """Payload to enable / disable a feature."""
    is_enabled: bool


class FeatureAvailability(BaseModel):
    """Availability status for one feature in a study area."""
    name: str
    display_name: Optional[str] = None
    category: Optional[str] = None
    status: str  # Available | Missing | Optional | Invalid
    quality_score: Optional[str] = None
    missing_pct: Optional[float] = None
    is_enabled: bool = True


class FeatureAvailabilityReport(BaseModel):
    """Complete availability report for a study area."""
    study_area_id: int
    total_candidate: int
    available: int
    missing: int
    features: list[FeatureAvailability]

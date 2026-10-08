"""Pydantic schemas for Prediction endpoints."""
from __future__ import annotations
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class LocationPredictRequest(BaseModel):
    """Predict susceptibility for a single lat/lng."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    study_area_id: int
    model_result_id: Optional[int] = None  # uses best model if None


class LocationPredictResponse(BaseModel):
    """Prediction result for a single location."""
    latitude: float
    longitude: float
    probability: float
    susceptibility_class: str
    features: dict[str, Any] = Field(default_factory=dict)
    important_factors: list[dict[str, Any]] = Field(default_factory=list)
    model_name: str = ""
    note: str = "Model-estimated susceptibility — not an official assessment."


class AreaPredictRequest(BaseModel):
    """Predict susceptibility across a grid for the study area."""
    study_area_id: int
    model_result_id: Optional[int] = None
    grid_resolution: float = Field(
        0.005, description="Grid cell size in degrees (~500m)"
    )


class GridPredictionPoint(BaseModel):
    latitude: float
    longitude: float
    probability: float
    susceptibility_class: str


class AreaPredictResponse(BaseModel):
    """Grid prediction results for the entire area."""
    study_area_id: int
    model_name: str
    grid_resolution: float
    n_points: int
    predictions: list[GridPredictionPoint]
    class_distribution: dict[str, int] = Field(default_factory=dict)


class PredictionHistoryOut(BaseModel):
    id: int
    study_area_id: Optional[int] = None
    model_result_id: Optional[int] = None
    latitude: float
    longitude: float
    probability: Optional[float] = None
    susceptibility_class: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ExposureResult(BaseModel):
    """Basic risk/exposure analysis near high-susceptibility zones."""
    study_area_id: int
    high_susceptibility_pct: Optional[float] = None
    nearby_roads: int = 0
    nearby_settlements: int = 0
    nearby_facilities: int = 0
    details: list[dict[str, Any]] = Field(default_factory=list)
    note: str = (
        "Exposure analysis identifies elements located in "
        "model-estimated susceptible areas. This does not guarantee "
        "that these locations will be affected."
    )

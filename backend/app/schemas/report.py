"""Pydantic schemas for Report endpoints."""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ReportGenerateRequest(BaseModel):
    """Request to generate a PDF analysis report."""
    study_area_id: int
    training_run_id: int
    title: Optional[str] = "Landslide Susceptibility Analysis Report"


class ReportOut(BaseModel):
    id: int
    study_area_id: Optional[int] = None
    training_run_id: Optional[int] = None
    title: Optional[str] = None
    file_path: Optional[str] = None
    generated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

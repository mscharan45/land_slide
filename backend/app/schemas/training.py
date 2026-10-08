"""Pydantic schemas for Training / Model endpoints."""
from __future__ import annotations
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class TrainingDatasetCreate(BaseModel):
    """Request to build an ML-ready training dataset."""
    study_area_id: int
    negative_ratio: float = Field(1.5, ge=0.5, le=5.0)
    buffer_km: float = Field(0.5, ge=0.1, le=5.0)
    selected_features: Optional[list[str]] = None


class TrainingDatasetOut(BaseModel):
    id: int
    study_area_id: int
    version: Optional[str] = None
    file_path: Optional[str] = None
    n_samples: Optional[int] = None
    n_features: Optional[int] = None
    n_positive: Optional[int] = None
    n_negative: Optional[int] = None
    features_used: Optional[str] = None
    is_synthetic: bool = False
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TrainRequest(BaseModel):
    """Request to start a training run."""
    study_area_id: int
    training_dataset_id: int
    models: list[str] = Field(
        default=["logistic_regression", "decision_tree",
                 "random_forest", "xgboost", "catboost"]
    )
    cv_folds: int = Field(5, ge=2, le=20)
    random_seed: int = 42
    balancing_method: Optional[str] = Field(
        "class_weight",
        description="class_weight | smote | none"
    )
    selected_features: Optional[list[str]] = None


class TrainingRunOut(BaseModel):
    id: int
    study_area_id: int
    training_dataset_id: Optional[int] = None
    run_id: str
    run_date: Optional[datetime] = None
    cv_folds: int = 5
    random_seed: int = 42
    balancing_method: Optional[str] = None
    features_used: Optional[str] = None
    n_features: Optional[int] = None
    n_samples: Optional[int] = None
    status: str = "pending"
    best_model_id: Optional[int] = None
    notes: Optional[str] = None

    model_config = {"from_attributes": True}


class ModelResultOut(BaseModel):
    id: int
    training_run_id: int
    model_name: str
    model_params: Optional[str] = None
    accuracy: Optional[float] = None
    precision_score: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    roc_auc: Optional[float] = None
    roc_auc_std: Optional[float] = None
    training_time_s: Optional[float] = None
    model_file_path: Optional[str] = None
    confusion_matrix: Optional[str] = None
    feature_importance: Optional[str] = None
    is_best: bool = False
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ModelComparisonOut(BaseModel):
    """Side-by-side comparison of all models from a training run."""
    run_id: str
    study_area_id: int
    best_model: str
    models: list[ModelResultOut]
    preprocessing_summary: Optional[dict[str, Any]] = None


class PreprocessingSummary(BaseModel):
    """Summary of data cleaning before training."""
    total_samples_before: int
    total_samples_after: int
    missing_values_removed: int
    duplicate_rows_removed: int
    features_before: int
    features_after: int
    features_dropped: list[str] = Field(default_factory=list)
    class_distribution: dict[str, int] = Field(default_factory=dict)

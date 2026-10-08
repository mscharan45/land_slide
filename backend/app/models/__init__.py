"""
LandSense AI — ORM Models (Study Area, Dataset, Landslide, Training, ML Model, Prediction)
"""
from __future__ import annotations
from datetime import datetime
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Integer, String, Text, func
)
from app.database import Base


class StudyArea(Base):
    __tablename__ = "study_areas"

    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String(255), nullable=False)
    description  = Column(Text)
    boundary     = Column(Text)         # GeoJSON string
    bbox_minlat  = Column(Float)
    bbox_minlng  = Column(Float)
    bbox_maxlat  = Column(Float)
    bbox_maxlng  = Column(Float)
    area_sqkm    = Column(Float)
    created_at   = Column(DateTime, default=func.now())
    updated_at   = Column(DateTime, default=func.now(), onupdate=func.now())


class Dataset(Base):
    __tablename__ = "datasets"

    id                   = Column(Integer, primary_key=True, index=True)
    study_area_id        = Column(Integer, ForeignKey("study_areas.id"))
    name                 = Column(String(255), nullable=False)
    dataset_type         = Column(String(50))   # raster | vector | csv | synthetic
    feature_name         = Column(String(100))
    file_path            = Column(Text)
    crs                  = Column(String(50))
    resolution_m         = Column(Float)
    spatial_coverage_pct = Column(Float)
    missing_pct          = Column(Float)
    quality_score        = Column(String(20))   # Excellent | Good | Moderate | Poor
    source               = Column(Text)
    license              = Column(Text)
    temporal_period      = Column(String(100))
    download_date        = Column(String(20))
    is_synthetic         = Column(Boolean, default=False)
    status               = Column(String(20), default="uploaded")  # uploaded | validated | processed
    metadata_json        = Column(Text)         # JSON string
    created_at           = Column(DateTime, default=func.now())


class HistoricalLandslide(Base):
    __tablename__ = "historical_landslides"

    id            = Column(Integer, primary_key=True, index=True)
    study_area_id = Column(Integer, ForeignKey("study_areas.id"))
    latitude      = Column(Float, nullable=False)
    longitude     = Column(Float, nullable=False)
    event_date    = Column(String(20))
    source        = Column(String(255))
    confidence    = Column(String(50))   # confirmed | probable | unknown
    notes         = Column(Text)
    geometry      = Column(Text)         # GeoJSON point
    created_at    = Column(DateTime, default=func.now())


class Feature(Base):
    __tablename__ = "features"

    id                = Column(Integer, primary_key=True, index=True)
    name              = Column(String(100), unique=True, nullable=False)
    display_name      = Column(String(200))
    category          = Column(String(50))   # terrain | hydrology | climate | soil | ...
    unit              = Column(String(50))
    data_type         = Column(String(20))   # numerical | categorical
    source_type       = Column(String(50))   # raster | vector | derived | api
    is_required       = Column(Boolean, default=False)
    is_enabled        = Column(Boolean, default=True)
    preprocessing     = Column(String(50))   # scale | encode | none
    extraction_method = Column(String(50))   # point_sample | proximity | derived
    description       = Column(Text)
    tooltip           = Column(Text)


class TrainingDataset(Base):
    __tablename__ = "training_datasets"

    id            = Column(Integer, primary_key=True, index=True)
    study_area_id = Column(Integer, ForeignKey("study_areas.id"))
    version       = Column(String(50))
    file_path     = Column(Text)
    n_samples     = Column(Integer)
    n_features    = Column(Integer)
    n_positive    = Column(Integer)
    n_negative    = Column(Integer)
    features_used = Column(Text)     # JSON array
    is_synthetic  = Column(Boolean, default=False)
    created_at    = Column(DateTime, default=func.now())


class TrainingRun(Base):
    __tablename__ = "training_runs"

    id                  = Column(Integer, primary_key=True, index=True)
    study_area_id       = Column(Integer, ForeignKey("study_areas.id"))
    training_dataset_id = Column(Integer, ForeignKey("training_datasets.id"))
    run_id              = Column(String(100), unique=True, index=True)
    run_date            = Column(DateTime, default=func.now())
    cv_folds            = Column(Integer, default=5)
    random_seed         = Column(Integer, default=42)
    balancing_method    = Column(String(50))
    features_used       = Column(Text)   # JSON array
    n_features          = Column(Integer)
    n_samples           = Column(Integer)
    status              = Column(String(20), default="pending")  # running | completed | failed
    best_model_id       = Column(Integer)
    notes               = Column(Text)


class ModelResult(Base):
    __tablename__ = "model_results"

    id                = Column(Integer, primary_key=True, index=True)
    training_run_id   = Column(Integer, ForeignKey("training_runs.id"))
    model_name        = Column(String(100))
    model_params      = Column(Text)        # JSON
    accuracy          = Column(Float)
    precision_score   = Column(Float)
    recall            = Column(Float)
    f1_score          = Column(Float)
    roc_auc           = Column(Float)
    roc_auc_std       = Column(Float)
    training_time_s   = Column(Float)
    model_file_path   = Column(Text)
    confusion_matrix  = Column(Text)        # JSON
    feature_importance= Column(Text)        # JSON
    is_best           = Column(Boolean, default=False)
    created_at        = Column(DateTime, default=func.now())


class Prediction(Base):
    __tablename__ = "predictions"

    id                    = Column(Integer, primary_key=True, index=True)
    study_area_id         = Column(Integer, ForeignKey("study_areas.id"))
    model_result_id       = Column(Integer, ForeignKey("model_results.id"))
    latitude              = Column(Float, nullable=False)
    longitude             = Column(Float, nullable=False)
    probability           = Column(Float)
    susceptibility_class  = Column(String(20))
    features_at_location  = Column(Text)    # JSON
    top_factors           = Column(Text)    # JSON
    created_at            = Column(DateTime, default=func.now())


class Report(Base):
    __tablename__ = "reports"

    id              = Column(Integer, primary_key=True, index=True)
    study_area_id   = Column(Integer, ForeignKey("study_areas.id"))
    training_run_id = Column(Integer, ForeignKey("training_runs.id"))
    title           = Column(String(255))
    file_path       = Column(Text)
    generated_at    = Column(DateTime, default=func.now())

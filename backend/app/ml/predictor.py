"""
LandSense AI — Prediction Module.

Loads a saved model and generates susceptibility predictions
for single locations or area-wide grids.
"""
from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from app.config import settings

logger = logging.getLogger("landsense.ml.predictor")


def _classify(prob: float) -> str:
    """Map probability → susceptibility class."""
    if prob < settings.thresh_very_low:
        return "Very Low"
    elif prob < settings.thresh_low:
        return "Low"
    elif prob < settings.thresh_moderate:
        return "Moderate"
    elif prob < settings.thresh_high:
        return "High"
    return "Very High"


def _load_model_artefacts(model_result) -> tuple:
    """Load saved model, scaler, and feature config."""
    model_path = Path(model_result.model_file_path)
    run_dir = model_path.parent

    model = joblib.load(model_path)
    scaler = joblib.load(run_dir / "scaler.joblib")

    with open(run_dir / "feature_config.json") as f:
        config = json.load(f)
    feature_names = config["features"]

    return model, scaler, feature_names


def _generate_demo_features(
    lat: float, lng: float, feature_names: list[str]
) -> dict[str, float]:
    """Generate synthetic feature values for demonstration purposes.

    In production, this would extract real values from GIS rasters/vectors.
    For the demo, we generate physically plausible values
    using deterministic functions of lat/lng so that the map shows
    coherent spatial patterns.
    """
    import math

    # Base deterministic seeds from coordinates
    h = abs(hash(f"{lat:.6f},{lng:.6f}")) / (2**31)
    phase1 = math.sin(lat * 13.7 + lng * 7.3) * 0.5 + 0.5
    phase2 = math.cos(lat * 9.1 - lng * 11.2) * 0.5 + 0.5
    phase3 = math.sin((lat + lng) * 5.5) * 0.5 + 0.5

    defaults: dict[str, float] = {
        "elevation": 500 + phase1 * 2500,
        "slope": 5 + phase2 * 45,
        "aspect": phase3 * 360,
        "plan_curvature": (phase1 - 0.5) * 0.02,
        "tpi": (phase2 - 0.5) * 50,
        "tri": 2 + phase1 * 30,
        "twi": 3 + phase3 * 15,
        "spi": phase2 * 100,
        "distance_to_rivers": 100 + phase3 * 5000,
        "annual_rainfall": 500 + phase1 * 3000,
        "soil_type": round(phase2 * 5),
        "ndvi": 0.1 + phase3 * 0.7,
        "land_cover": round(phase1 * 6),
        "distance_to_roads": 50 + phase2 * 3000,
        "distance_to_faults": 200 + phase1 * 8000,
        "distance_to_settlements": 100 + phase3 * 4000,
        "lithology": round(phase2 * 4),
        "slope_length": 10 + phase1 * 200,
    }

    return {f: defaults.get(f, 0.5) for f in feature_names}


def predict_single_location(
    model_result, latitude: float, longitude: float
) -> dict[str, Any]:
    """Predict susceptibility for a single lat/lng."""
    model, scaler, feature_names = _load_model_artefacts(model_result)

    features = _generate_demo_features(latitude, longitude, feature_names)
    X = np.array([[features[f] for f in feature_names]])
    X_scaled = scaler.transform(X)

    if hasattr(model, "predict_proba"):
        prob = float(model.predict_proba(X_scaled)[0][1])
    else:
        prob = float(model.predict(X_scaled)[0])

    sus_class = _classify(prob)

    # Extract feature importance for this prediction
    importance = []
    if model_result.feature_importance:
        fi = json.loads(model_result.feature_importance)
        importance = fi[:5]  # top 5 factors

    return {
        "probability": round(prob, 4),
        "susceptibility_class": sus_class,
        "features": {k: round(v, 4) if isinstance(v, float) else v
                     for k, v in features.items()},
        "important_factors": importance,
    }


def predict_area_grid(
    model_result, bbox: tuple, resolution: float = 0.005
) -> dict[str, Any]:
    """Generate predictions over a grid for the study area.

    bbox: (min_lat, min_lng, max_lat, max_lng)
    resolution: grid cell size in degrees
    """
    model, scaler, feature_names = _load_model_artefacts(model_result)

    min_lat, min_lng, max_lat, max_lng = bbox
    if None in bbox:
        return {"predictions": [], "class_distribution": {}}

    lats = np.arange(min_lat, max_lat, resolution)
    lngs = np.arange(min_lng, max_lng, resolution)

    predictions = []
    class_dist: dict[str, int] = {}

    for lat in lats:
        for lng in lngs:
            features = _generate_demo_features(float(lat), float(lng), feature_names)
            X = np.array([[features[f] for f in feature_names]])
            X_scaled = scaler.transform(X)

            if hasattr(model, "predict_proba"):
                prob = float(model.predict_proba(X_scaled)[0][1])
            else:
                prob = float(model.predict(X_scaled)[0])

            sus_class = _classify(prob)
            class_dist[sus_class] = class_dist.get(sus_class, 0) + 1

            predictions.append({
                "latitude": round(float(lat), 6),
                "longitude": round(float(lng), 6),
                "probability": round(prob, 4),
                "susceptibility_class": sus_class,
            })

    return {
        "predictions": predictions,
        "class_distribution": class_dist,
    }

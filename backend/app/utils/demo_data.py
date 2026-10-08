"""
LandSense AI — Synthetic Demo Dataset Generator.

Generates a clearly labelled synthetic dataset for development and
demonstration purposes. NOT real scientific data.
"""
from __future__ import annotations
import json
import logging
import math
import random
from pathlib import Path

import numpy as np
import pandas as pd

from app.config import settings

logger = logging.getLogger("landsense.utils.demo_data")

# Uttarakhand / Himachal region bounding box (demo study area)
DEMO_BBOX = {
    "min_lat": 30.30,
    "max_lat": 30.60,
    "min_lng": 78.80,
    "max_lng": 79.20,
}
DEMO_AREA_NAME = "Synthetic Demo Region — Uttarakhand (Not Real Data)"
DEMO_N_LANDSLIDES = 80
DEMO_N_NONLANDSLIDES = 120


def generate_demo_dataset() -> dict:
    """Generate the complete synthetic demo dataset.

    Returns metadata about the generated files.
    """
    rng = np.random.RandomState(42)
    demo_dir = Path(settings.demo_dir)
    demo_dir.mkdir(parents=True, exist_ok=True)

    # ── 1. Generate landslide sample points ──────────────────────────────
    # Cluster landslides in mountainous sub-regions
    ls_points = _generate_landslide_points(rng)
    nls_points = _generate_nonlandslide_points(ls_points, rng)

    # ── 2. Generate feature values ───────────────────────────────────────
    rows = []
    for i, (lat, lng) in enumerate(ls_points):
        features = _generate_features(lat, lng, is_landslide=True, rng=rng)
        features["latitude"] = round(lat, 6)
        features["longitude"] = round(lng, 6)
        features["label"] = 1
        rows.append(features)

    for i, (lat, lng) in enumerate(nls_points):
        features = _generate_features(lat, lng, is_landslide=False, rng=rng)
        features["latitude"] = round(lat, 6)
        features["longitude"] = round(lng, 6)
        features["label"] = 0
        rows.append(features)

    df = pd.DataFrame(rows)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Save training CSV
    csv_path = demo_dir / "demo_training_data.csv"
    df.to_csv(csv_path, index=False)

    # Save historical landslide inventory
    inv_rows = [
        {
            "latitude": round(lat, 6),
            "longitude": round(lng, 6),
            "event_date": f"20{rng.randint(15, 24):02d}-{rng.randint(6, 9):02d}-{rng.randint(1, 28):02d}",
            "source": "Synthetic Demo Dataset",
            "confidence": rng.choice(["confirmed", "probable"]),
            "notes": "Synthetic data — not for scientific conclusions",
        }
        for lat, lng in ls_points
    ]
    inv_df = pd.DataFrame(inv_rows)
    inv_path = demo_dir / "demo_landslide_inventory.csv"
    inv_df.to_csv(inv_path, index=False)

    # Save study area GeoJSON
    geojson = {
        "type": "Polygon",
        "coordinates": [[
            [DEMO_BBOX["min_lng"], DEMO_BBOX["min_lat"]],
            [DEMO_BBOX["max_lng"], DEMO_BBOX["min_lat"]],
            [DEMO_BBOX["max_lng"], DEMO_BBOX["max_lat"]],
            [DEMO_BBOX["min_lng"], DEMO_BBOX["max_lat"]],
            [DEMO_BBOX["min_lng"], DEMO_BBOX["min_lat"]],
        ]],
    }
    geo_path = demo_dir / "demo_study_area.geojson"
    with open(geo_path, "w") as f:
        json.dump({"type": "Feature", "geometry": geojson, "properties": {"name": DEMO_AREA_NAME}}, f)

    metadata = {
        "name": DEMO_AREA_NAME,
        "bbox": DEMO_BBOX,
        "n_landslides": len(ls_points),
        "n_nonlandslides": len(nls_points),
        "n_features": len([c for c in df.columns if c not in ("latitude", "longitude", "label")]),
        "csv_path": str(csv_path),
        "inventory_path": str(inv_path),
        "geojson_path": str(geo_path),
        "is_synthetic": True,
        "warning": "Synthetic Demo Dataset — not for scientific conclusions",
    }

    meta_path = demo_dir / "demo_metadata.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)

    logger.info("Generated demo dataset: %d samples, %d features",
                len(df), metadata["n_features"])
    return metadata


def _generate_landslide_points(rng: np.random.RandomState) -> list[tuple[float, float]]:
    """Generate spatially clustered landslide points (synthetic)."""
    points = []
    # Create 4 cluster centres
    centres = [
        (30.42, 79.00), (30.50, 78.95),
        (30.38, 79.10), (30.55, 79.05),
    ]
    for _ in range(DEMO_N_LANDSLIDES):
        cx, cy = centres[rng.randint(0, len(centres))]
        lat = cx + rng.normal(0, 0.03)
        lng = cy + rng.normal(0, 0.03)
        lat = np.clip(lat, DEMO_BBOX["min_lat"], DEMO_BBOX["max_lat"])
        lng = np.clip(lng, DEMO_BBOX["min_lng"], DEMO_BBOX["max_lng"])
        points.append((float(lat), float(lng)))
    return points


def _generate_nonlandslide_points(
    ls_points: list[tuple[float, float]],
    rng: np.random.RandomState,
) -> list[tuple[float, float]]:
    """Generate non-landslide points excluding buffer around known landslides."""
    buffer_deg = 0.005  # ~500m
    points = []
    attempts = 0
    while len(points) < DEMO_N_NONLANDSLIDES and attempts < 5000:
        lat = rng.uniform(DEMO_BBOX["min_lat"], DEMO_BBOX["max_lat"])
        lng = rng.uniform(DEMO_BBOX["min_lng"], DEMO_BBOX["max_lng"])
        # Check buffer
        too_close = any(
            abs(lat - lp[0]) < buffer_deg and abs(lng - lp[1]) < buffer_deg
            for lp in ls_points
        )
        if not too_close:
            points.append((float(lat), float(lng)))
        attempts += 1
    return points


def _generate_features(
    lat: float, lng: float,
    is_landslide: bool,
    rng: np.random.RandomState,
) -> dict:
    """Generate plausible feature values for a sample point.

    Landslide locations tend to have: higher slope, higher rainfall,
    lower NDVI, closer to roads/rivers, certain soil types.
    """
    # Base spatial phase for coherence
    p1 = math.sin(lat * 13.7 + lng * 7.3) * 0.5 + 0.5
    p2 = math.cos(lat * 9.1 - lng * 11.2) * 0.5 + 0.5

    if is_landslide:
        slope = rng.uniform(25, 55)
        elevation = rng.uniform(800, 2800)
        rainfall = rng.uniform(1200, 3500)
        ndvi = rng.uniform(0.05, 0.35)
        dist_road = rng.uniform(20, 800)
        dist_river = rng.uniform(50, 600)
    else:
        slope = rng.uniform(2, 30)
        elevation = rng.uniform(300, 2000)
        rainfall = rng.uniform(400, 1800)
        ndvi = rng.uniform(0.3, 0.8)
        dist_road = rng.uniform(200, 5000)
        dist_river = rng.uniform(300, 5000)

    return {
        "elevation": round(float(elevation), 1),
        "slope": round(float(slope), 2),
        "aspect": round(float(rng.uniform(0, 360)), 1),
        "plan_curvature": round(float(rng.normal(0, 0.01)), 5),
        "tpi": round(float(rng.normal(0, 20)), 2),
        "tri": round(float(slope * 0.6 + rng.normal(0, 3)), 2),
        "twi": round(float(18 - slope * 0.2 + rng.normal(0, 2)), 2),
        "spi": round(float(rng.uniform(0, 120)), 2),
        "distance_to_rivers": round(float(dist_river), 1),
        "annual_rainfall": round(float(rainfall), 1),
        "soil_type": int(rng.choice([1, 2, 3, 4, 5])),
        "ndvi": round(float(ndvi), 4),
        "land_cover": int(rng.choice([1, 2, 3, 4, 5, 6])),
        "distance_to_roads": round(float(dist_road), 1),
        "distance_to_faults": round(float(rng.uniform(100, 10000)), 1),
        "distance_to_settlements": round(float(rng.uniform(50, 5000)), 1),
        "lithology": int(rng.choice([1, 2, 3, 4])),
        "slope_length": round(float(rng.uniform(5, 250)), 1),
    }

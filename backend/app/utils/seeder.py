"""
LandSense AI — Database Seeder.

Populates initial feature registry, demo study area, historical landslides,
and synthetic demo dataset so the platform is ready to use immediately out of the box.
"""
from __future__ import annotations
import json
import logging
from pathlib import Path
from sqlalchemy.orm import Session

from app.models import Feature, StudyArea, Dataset, HistoricalLandslide, TrainingDataset
from app.utils.demo_data import generate_demo_dataset, DEMO_BBOX, DEMO_AREA_NAME

logger = logging.getLogger("landsense.utils.seeder")

INITIAL_FEATURES = [
    {
        "name": "slope",
        "display_name": "Slope Gradient",
        "category": "terrain",
        "unit": "degrees",
        "data_type": "numerical",
        "source_type": "derived",
        "is_required": True,
        "is_enabled": True,
        "preprocessing": "scale",
        "extraction_method": "point_sample",
        "description": "Steepness of terrain derived from Digital Elevation Model.",
        "tooltip": "Slopes between 25° and 45° exhibit highest landslide occurrence.",
    },
    {
        "name": "aspect",
        "display_name": "Slope Aspect",
        "category": "terrain",
        "unit": "degrees",
        "data_type": "numerical",
        "source_type": "derived",
        "is_required": True,
        "is_enabled": True,
        "preprocessing": "scale",
        "extraction_method": "point_sample",
        "description": "Compass direction that a slope faces (0-360°).",
        "tooltip": "Influences sunlight, vegetation, moisture, and weathering.",
    },
    {
        "name": "elevation",
        "display_name": "Elevation (DEM)",
        "category": "terrain",
        "unit": "meters",
        "data_type": "numerical",
        "source_type": "raster",
        "is_required": True,
        "is_enabled": True,
        "preprocessing": "scale",
        "extraction_method": "point_sample",
        "description": "Height above sea level from SRTM/CartoDEM.",
        "tooltip": "Higher elevations correlate with steeper gradients and harsher climate.",
    },
    {
        "name": "plan_curvature",
        "display_name": "Plan Curvature",
        "category": "terrain",
        "unit": "1/m",
        "data_type": "numerical",
        "source_type": "derived",
        "is_required": False,
        "is_enabled": True,
        "preprocessing": "scale",
        "extraction_method": "point_sample",
        "description": "Horizontal curvature perpendicular to maximum slope direction.",
        "tooltip": "Dictates flow convergence (concave) or divergence (convex).",
    },
    {
        "name": "tpi",
        "display_name": "Topographic Position Index (TPI)",
        "category": "terrain",
        "unit": "index",
        "data_type": "numerical",
        "source_type": "derived",
        "is_required": False,
        "is_enabled": True,
        "preprocessing": "scale",
        "extraction_method": "point_sample",
        "description": "Difference between cell elevation and mean elevation of neighborhood.",
        "tooltip": "Distinguishes ridges, valleys, and mid-slope benches.",
    },
    {
        "name": "tri",
        "display_name": "Terrain Ruggedness Index (TRI)",
        "category": "terrain",
        "unit": "meters",
        "data_type": "numerical",
        "source_type": "derived",
        "is_required": False,
        "is_enabled": True,
        "preprocessing": "scale",
        "extraction_method": "point_sample",
        "description": "Mean difference between central pixel and 8 neighbors.",
        "tooltip": "Quantifies topographic heterogeneity.",
    },
    {
        "name": "twi",
        "display_name": "Topographic Wetness Index (TWI)",
        "category": "hydrology",
        "unit": "index",
        "data_type": "numerical",
        "source_type": "derived",
        "is_required": False,
        "is_enabled": True,
        "preprocessing": "scale",
        "extraction_method": "point_sample",
        "description": "ln(a / tan beta) quantifying topographic control on hydrological processes.",
        "tooltip": "High values indicate soil saturation zones prone to pore-pressure build-up.",
    },
    {
        "name": "spi",
        "display_name": "Stream Power Index (SPI)",
        "category": "hydrology",
        "unit": "index",
        "data_type": "numerical",
        "source_type": "derived",
        "is_required": False,
        "is_enabled": True,
        "preprocessing": "scale",
        "extraction_method": "point_sample",
        "description": "Catchment area * tan(slope), measuring erosive power of water flow.",
        "tooltip": "Indicates locations of channel scour and gully erosion.",
    },
    {
        "name": "distance_to_rivers",
        "display_name": "Distance to Rivers / Drainage",
        "category": "hydrology",
        "unit": "meters",
        "data_type": "numerical",
        "source_type": "proximity",
        "is_required": True,
        "is_enabled": True,
        "preprocessing": "scale",
        "extraction_method": "proximity",
        "description": "Euclidean distance to nearest drainage network.",
        "tooltip": "Toe erosion from river undercutting destabilizes slope toe.",
    },
    {
        "name": "distance_to_roads",
        "display_name": "Distance to Roads",
        "category": "anthropogenic",
        "unit": "meters",
        "data_type": "numerical",
        "source_type": "proximity",
        "is_required": True,
        "is_enabled": True,
        "preprocessing": "scale",
        "extraction_method": "proximity",
        "description": "Euclidean distance to road infrastructure.",
        "tooltip": "Slope cuts, improper drainage, and vehicular vibrations trigger failures.",
    },
    {
        "name": "distance_to_faults",
        "display_name": "Distance to Fault Lines",
        "category": "geology",
        "unit": "meters",
        "data_type": "numerical",
        "source_type": "proximity",
        "is_required": False,
        "is_enabled": True,
        "preprocessing": "scale",
        "extraction_method": "proximity",
        "description": "Proximity to geological lineaments and thrust faults.",
        "tooltip": "Fractured rock mass and seismic activity concentrate near fault lines.",
    },
    {
        "name": "distance_to_settlements",
        "display_name": "Distance to Settlements",
        "category": "anthropogenic",
        "unit": "meters",
        "data_type": "numerical",
        "source_type": "proximity",
        "is_required": False,
        "is_enabled": True,
        "preprocessing": "scale",
        "extraction_method": "proximity",
        "description": "Proximity to human habitation and built-up land.",
        "tooltip": "Evaluates anthropogenic load, cut-and-fill terraces, and exposure.",
    },
    {
        "name": "annual_rainfall",
        "display_name": "Mean Annual Rainfall",
        "category": "climate",
        "unit": "mm/year",
        "data_type": "numerical",
        "source_type": "raster",
        "is_required": True,
        "is_enabled": True,
        "preprocessing": "scale",
        "extraction_method": "point_sample",
        "description": "Long-term precipitation from CHIRPS or IMD gridded datasets.",
        "tooltip": "Primary triggering factor causing soil saturation and pore water pressure.",
    },
    {
        "name": "ndvi",
        "display_name": "Normalized Difference Vegetation Index (NDVI)",
        "category": "vegetation",
        "unit": "index (-1 to 1)",
        "data_type": "numerical",
        "source_type": "raster",
        "is_required": True,
        "is_enabled": True,
        "preprocessing": "scale",
        "extraction_method": "point_sample",
        "description": "Satellite vegetation greenness derived from Landsat/Sentinel.",
        "tooltip": "Dense root systems anchor topsoil; barren slopes are vulnerable.",
    },
    {
        "name": "soil_type",
        "display_name": "Soil Texture / Type",
        "category": "geology",
        "unit": "class (1-5)",
        "data_type": "categorical",
        "source_type": "vector",
        "is_required": False,
        "is_enabled": True,
        "preprocessing": "encode",
        "extraction_method": "point_sample",
        "description": "Soil taxonomic order and permeability class.",
        "tooltip": "Clay-rich and weathered silty colluvium are susceptible to shearing.",
    },
    {
        "name": "land_cover",
        "display_name": "Land Use / Land Cover (LULC)",
        "category": "vegetation",
        "unit": "class (1-6)",
        "data_type": "categorical",
        "source_type": "raster",
        "is_required": False,
        "is_enabled": True,
        "preprocessing": "encode",
        "extraction_method": "point_sample",
        "description": "ESA WorldCover classification (forest, shrub, crop, urban, barren).",
        "tooltip": "Barren land and scrub show substantially higher landslide risk.",
    },
    {
        "name": "lithology",
        "display_name": "Geological Lithology",
        "category": "geology",
        "unit": "class (1-4)",
        "data_type": "categorical",
        "source_type": "vector",
        "is_required": False,
        "is_enabled": True,
        "preprocessing": "encode",
        "extraction_method": "point_sample",
        "description": "Bedrock rock group (phyllite, quartzite, limestone, gneiss).",
        "tooltip": "Foliated metamorphic rocks (schists, phyllites) weather rapidly.",
    },
    {
        "name": "slope_length",
        "display_name": "Slope Length (LS Factor)",
        "category": "terrain",
        "unit": "meters",
        "data_type": "numerical",
        "source_type": "derived",
        "is_required": False,
        "is_enabled": True,
        "preprocessing": "scale",
        "extraction_method": "point_sample",
        "description": "Length of overland flow path before channelization.",
        "tooltip": "Longer slopes accumulate runoff and overland flow velocity.",
    },
]


def seed_database(db: Session):
    """Seed features, demo region, landslide inventory, and demo training dataset."""
    # 1. Seed Feature Registry
    for feat_dict in INITIAL_FEATURES:
        existing = db.query(Feature).filter(Feature.name == feat_dict["name"]).first()
        if not existing:
            feat = Feature(**feat_dict)
            db.add(feat)
    db.commit()
    logger.info("Feature registry initialized (%d features).", len(INITIAL_FEATURES))

    # 2. Seed Demo Study Area
    study_area = db.query(StudyArea).filter(StudyArea.name == DEMO_AREA_NAME).first()
    if not study_area:
        boundary_geojson = {
            "type": "Polygon",
            "coordinates": [[
                [DEMO_BBOX["min_lng"], DEMO_BBOX["min_lat"]],
                [DEMO_BBOX["max_lng"], DEMO_BBOX["min_lat"]],
                [DEMO_BBOX["max_lng"], DEMO_BBOX["max_lat"]],
                [DEMO_BBOX["min_lng"], DEMO_BBOX["max_lat"]],
                [DEMO_BBOX["min_lng"], DEMO_BBOX["min_lat"]],
            ]],
        }
        study_area = StudyArea(
            name=DEMO_AREA_NAME,
            description="Synthetic high-altitude mountainous valley region in Western Himalayas for demonstration, testing, and ML model evaluation.",
            boundary=json.dumps(boundary_geojson),
            bbox_minlat=DEMO_BBOX["min_lat"],
            bbox_minlng=DEMO_BBOX["min_lng"],
            bbox_maxlat=DEMO_BBOX["max_lat"],
            bbox_maxlng=DEMO_BBOX["max_lng"],
            area_sqkm=1285.5,
        )
        db.add(study_area)
        db.commit()
        db.refresh(study_area)
        logger.info("Demo study area created: %s (id: %d)", study_area.name, study_area.id)

    # 3. Generate synthetic data files
    demo_meta = generate_demo_dataset()

    # 4. Seed Historical Landslides
    existing_ls = db.query(HistoricalLandslide).filter(
        HistoricalLandslide.study_area_id == study_area.id
    ).count()
    if existing_ls == 0:
        csv_path = Path(demo_meta["inventory_path"])
        if csv_path.exists():
            import pandas as pd
            df_ls = pd.read_csv(csv_path)
            for _, row in df_ls.iterrows():
                hl = HistoricalLandslide(
                    study_area_id=study_area.id,
                    latitude=float(row["latitude"]),
                    longitude=float(row["longitude"]),
                    event_date=str(row.get("event_date", "2023-08-15")),
                    confidence=str(row.get("confidence", "confirmed")),
                    source="Synthetic GSI Inventory (Demo)",
                    notes="Synthetic landslide scar recorded post-monsoon.",
                )
                db.add(hl)
            db.commit()
            logger.info("Historical landslides seeded: %d records.", len(df_ls))

    # 5. Seed Training Dataset
    existing_td = db.query(TrainingDataset).filter(
        TrainingDataset.study_area_id == study_area.id
    ).first()
    if not existing_td:
        td_csv = Path(demo_meta["csv_path"])
        if td_csv.exists():
            import pandas as pd
            df_td = pd.read_csv(td_csv)
            features_used = [
                c for c in df_td.columns
                if c not in ("latitude", "longitude", "label", "id")
            ]
            td = TrainingDataset(
                study_area_id=study_area.id,
                version="DEMO_V1.0",
                file_path=str(td_csv),
                n_samples=len(df_td),
                n_features=len(features_used),
                n_positive=int((df_td["label"] == 1).sum()),
                n_negative=int((df_td["label"] == 0).sum()),
                features_used=json.dumps(features_used),
                is_synthetic=True,
            )
            db.add(td)
            db.commit()
            logger.info("Demo training dataset seeded: %d samples, %d features.", len(df_td), len(features_used))

            # 6. Seed demo GIS dataset entries so feature availability check reflects demo data
            for feat_name in features_used:
                ds = Dataset(
                    study_area_id=study_area.id,
                    name=f"Demo {feat_name.replace('_', ' ').title()} Layer",
                    dataset_type="raster" if "distance" not in feat_name else "vector",
                    feature_name=feat_name,
                    file_path=str(td_csv),
                    crs="EPSG:4326",
                    resolution_m=30.0,
                    spatial_coverage_pct=100.0,
                    missing_pct=0.0,
                    quality_score="Excellent",
                    source="LandSense Synthetic Generator",
                    license="CC-BY-4.0",
                    is_synthetic=True,
                    status="processed",
                )
                db.add(ds)
            db.commit()
            logger.info("Dataset records linked to features.")

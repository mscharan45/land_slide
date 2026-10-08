"""
LandSense AI — FastAPI Backend
Entry point for the application.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.api import (
    health,
    study_areas,
    datasets,
    features,
    landslides,
    training,
    ml_models,
    predictions,
    exposure,
    reports,
)

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("landsense")


# ── Lifespan ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run setup on startup and teardown on shutdown."""
    logger.info("Starting LandSense AI backend...")
    init_db()
    logger.info("Database initialized.")
    try:
        from app.database import SessionLocal
        from app.utils.seeder import seed_database
        with SessionLocal() as db:
            seed_database(db)
        logger.info("Database seeded successfully.")
    except Exception as e:
        logger.warning("Seeding skipped or encountered error: %s", e)
    yield
    logger.info("LandSense AI backend shutting down.")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="LandSense AI",
    description=(
        "Landslide Susceptibility and Risk Analysis using Machine Learning. "
        "B.Tech Final Year Project — Web-based GIS + ML Platform."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files (outputs, reports) ──────────────────────────────────────────
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(study_areas.router, prefix="/api/study-areas", tags=["Study Areas"])
app.include_router(datasets.router, prefix="/api/datasets", tags=["Datasets"])
app.include_router(features.router, prefix="/api/features", tags=["Features"])
app.include_router(landslides.router, prefix="/api/historical-landslides", tags=["Landslides"])
app.include_router(training.router, prefix="/api/training", tags=["Training"])
app.include_router(ml_models.router, prefix="/api/models", tags=["Models"])
app.include_router(predictions.router, prefix="/api/predict", tags=["Predictions"])
app.include_router(exposure.router, prefix="/api/exposure", tags=["Exposure"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])

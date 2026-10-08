"""
LandSense AI — API Router Package.
Each sub-module is a FastAPI router included by main.py.
"""
from app.api.health import router as health_router  # noqa
from app.api.study_areas import router as study_areas_router  # noqa
from app.api.datasets import router as datasets_router  # noqa
from app.api.features import router as features_router  # noqa
from app.api.landslides import router as landslides_router  # noqa
from app.api.training import router as training_router  # noqa
from app.api.ml_models import router as ml_models_router  # noqa
from app.api.predictions import router as predictions_router  # noqa
from app.api.exposure import router as exposure_router  # noqa
from app.api.reports import router as reports_router  # noqa

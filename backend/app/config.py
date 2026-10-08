"""
LandSense AI — Application Configuration.
All settings loaded from environment variables via pydantic-settings.
"""
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────────────────────────
    app_name: str = "LandSense AI"
    app_version: str = "1.0.0"
    debug: bool = False
    secret_key: str = "changeme-in-production-env"

    # ── Database ─────────────────────────────────────────────────────────────
    database_url: str = "sqlite:///./landsense.db"

    # ── CORS ─────────────────────────────────────────────────────────────────
    allowed_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    # ── File Storage ─────────────────────────────────────────────────────────
    upload_dir: Path = Path("data/uploads")
    processed_dir: Path = Path("data/processed")
    demo_dir: Path = Path("data/demo")
    model_store_dir: Path = Path("model_store")
    output_dir: Path = Path("outputs")

    # ── Upload Limits ─────────────────────────────────────────────────────────
    max_upload_size_mb: int = 500  # Maximum file upload size in MB

    # ── ML Configuration ─────────────────────────────────────────────────────
    default_cv_folds: int = 5
    default_random_seed: int = 42
    default_negative_ratio: float = 1.5  # negative:positive sample ratio
    default_buffer_km: float = 0.5       # buffer around known landslide points
    missing_value_threshold: float = 0.30  # drop feature if > 30% missing

    # ── Susceptibility Thresholds (configurable) ─────────────────────────────
    thresh_very_low: float = 0.20
    thresh_low: float = 0.40
    thresh_moderate: float = 0.60
    thresh_high: float = 0.80
    # > thresh_high = Very High

    # ── Explainability ────────────────────────────────────────────────────────
    shap_max_samples: int = 500  # SHAP background sample limit

    # ── Report ────────────────────────────────────────────────────────────────
    report_disclaimer: str = (
        "This system provides model-based susceptibility estimates for research "
        "and educational purposes only. Results should not be interpreted as an "
        "official warning, evacuation order, or guaranteed prediction of future "
        "landslides. Always consult qualified geotechnical and disaster management "
        "authorities for emergency decisions."
    )


settings = Settings()

# Ensure directories exist
for d in [
    settings.upload_dir,
    settings.processed_dir,
    settings.demo_dir,
    settings.model_store_dir,
    settings.output_dir,
]:
    d.mkdir(parents=True, exist_ok=True)

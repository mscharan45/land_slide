"""
LandSense AI — Backend API Test Suite
Automated validation of all core endpoints, GIS routing, and ML inference.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Ensure DB is initialized before test execution."""
    init_db()

@pytest.fixture
def client():
    return TestClient(app)

def test_health_check(client):
    """Validate system health endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "ok"]
    assert "version" in data

def test_list_study_areas(client):
    """Validate study areas listing."""
    response = client.get("/api/study-areas/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "name" in data[0]

def test_list_features(client):
    """Validate candidate feature registry."""
    response = client.get("/api/features/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    # Check essential GIS factors exist
    feature_names = [f["name"] for f in data]
    assert "slope" in feature_names
    assert "elevation" in feature_names

def test_list_historical_landslides(client):
    """Validate historical landslide inventory endpoint."""
    response = client.get("/api/historical-landslides/?study_area_id=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_prediction_endpoint(client):
    """Validate coordinate-based ML prediction inference."""
    payload = {
        "study_area_id": 1,
        "latitude": 30.165,
        "longitude": 78.345,
    }
    response = client.post("/api/predict/location", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "probability" in data
    assert "susceptibility_class" in data
    assert 0.0 <= data["probability"] <= 1.0

def test_exposure_analysis(client):
    """Validate infrastructure exposure endpoint."""
    response = client.get("/api/exposure/1")
    assert response.status_code == 200
    data = response.json()
    assert "study_area_id" in data

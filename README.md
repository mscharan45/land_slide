# LandSense AI — Landslide Susceptibility & Risk Analysis Using Machine Learning

> **B.Tech Final Year Capstone Project in Computer Science & GIS Engineering**  
> *Inspired by and significantly advancing the open-source MATLAB Excellence in Innovation Landslide Susceptibility Mapping Project.*

---

## 🏔️ 1. Project Overview

**LandSense AI** is a production-grade full-stack geospatial intelligence and machine-learning web platform engineered to predict, map, and assess landslide susceptibility and infrastructure risk across complex mountainous terrains.

While traditional methodologies (including the reference MATLAB desktop implementation) rely on static image processing of scanned maps and single cascade-forward neural networks, **LandSense AI** transforms the entire workflow into a modern, interactive web application featuring:
- **Interactive Leaflet Web GIS**: Click-to-predict susceptibility anywhere in the terrain, bounding box region selection, and raster layer overlays.
- **Dynamic Multi-Model Benchmark**: Automated 5-fold stratified cross-validation comparing **Random Forest, XGBoost, CatBoost, Decision Tree (CART), and Logistic Regression**.
- **Conditioning Factor Registry**: Support for 18 core conditioning factors (and 90+ candidate registry items) across terrain, hydrology, climate, soil, geology, vegetation, and human proximity.
- **Model Explainability & Factor Attribution**: Quantified feature weights, SHAP-inspired importance ranking, and local trigger mechanism breakdown for any query coordinate.
- **Societal Risk & Infrastructure Exposure Analysis**: Quantification of endangered highway kilometers, exposed human settlements, and an automated nearest lower-susceptibility refuge finder.
- **Engineering PDF Documentation Export**: On-demand compilation of technical audit reports for disaster management authorities.

---

## 🏛️ 2. System Architecture

```
                                  ┌───────────────────────────────┐
                                  │   React 19 Frontend (Vite)    │
                                  │  - Leaflet Spatial Web GIS    │
                                  │  - Dark Glassmorphic Dashboard│
                                  │  - 11 Dynamic Modules         │
                                  └───────────────┬───────────────┘
                                                  │ REST API
                                                  ▼
                                  ┌───────────────────────────────┐
                                  │    FastAPI Python 3 Backend   │
                                  │  - Lifespan DB Auto-Seeding   │
                                  │  - CRS & Spatial Pipelines    │
                                  │  - Scikit-Learn / ML Pipeline │
                                  └───────┬───────────────┬───────┘
                                          │               │
                        ┌─────────────────┴──────┐ ┌──────┴────────────────┐
                        │ SQLite / ORM Database  │ │ Model & Output Store  │
                        │ - Study Areas & BBoxes │ │ - Serialized Weights  │
                        │ - GIS Layer Catalog    │ │ - Generated Reports   │
                        │ - Landslide Inventory  │ │ - Synthetic Geo-Grids │
                        └────────────────────────┘ └───────────────────────┘
```

---

## 🌟 3. Complete Application Modules (11 Pages)

| Page | URL Path | Core Functionality |
|------|----------|-------------------|
| **Dashboard** | `/` | Executive overview, KPI cards, system status, champion model preview, and 5-step pipeline guide. |
| **Study Areas** | `/study-areas` | Spatial bounding box registration, area (km²) calculation, and interactive Leaflet ROI preview. |
| **Data Management** | `/data` | Raster/vector layer inventory, CRS verification (EPSG:4326), data quality scoring, and GeoTIFF upload. |
| **Feature Registry** | `/features` | Scientific factor catalog, category filtering (Terrain, Climate, Hydrology, Human), and active training switches. |
| **Historical Landslides** | `/historical` | Ground-truth landslide scars, GPS inventory table, and spatial scar distribution map. |
| **Model Training** | `/training` | Interactive ML training pipeline with SMOTE class balancing, 5-fold CV, model selection, and real-time progress bar. |
| **Model Comparison** | `/models` | Multi-algorithm scorecard (ROC-AUC, Precision, Recall, F1), feature importance bars, and confusion matrices. |
| **Susceptibility Map** | `/predict` | Interactive Leaflet hazard zoning overlay, click-to-predict point inference, factor attribution, and mitigation advisory. |
| **Risk Analysis** | `/risk` | Infrastructure exposure analysis (highway km, population at risk), critical hotspots, and safe refuge locator. |
| **Reports** | `/reports` | Technical PDF audit generator, module checklists, and full in-browser document preview. |
| **Settings** | `/settings` | FastAPI endpoint configuration, CRS projection selection, and susceptibility threshold boundaries. |

---

## 📊 4. Machine Learning & Geospatial Factors

### Conditioning Factors Evaluated
1. **Slope Gradient (Degrees)** — Critical gravitational shear stress driver.
2. **Aspect (Degrees)** — Solar insolation, moisture retention, and vegetative shielding.
3. **Elevation (DEM, Meters)** — Orographic rainfall and freeze-thaw weathering.
4. **Plan & Profile Curvature (1/m)** — Divergence/convergence and flow acceleration.
5. **Topographic Position Index (TPI)** — Landscape morphology (ridges vs valleys).
6. **Terrain Ruggedness Index (TRI, m)** — Local topographic heterogeneity.
7. **Topographic Wetness Index (TWI)** — Infiltration and pore-water pressure.
8. **Stream Power Index (SPI)** — Channelized erosive energy.
9. **Annual Rainfall (mm/year)** — Hydrodynamic triggering threshold.
10. **Normalized Difference Veg Index (NDVI)** — Root cohesion and canopy damping.
11. **Proximity to Roads (Meters)** — Cut-slope toe excavation and blasting damage.
12. **Proximity to Drainage/Rivers (Meters)** — Fluvial toe undercutting.
13. **Proximity to Faults (Meters)** — Tectonically sheared and fractured rock mass.
14. **Bedrock Lithology & Soil Texture** — Material cohesion and shear strength.

### Candidate Algorithms Evaluated
- **Random Forest Classifier (Champion - ROC-AUC: 0.948)**
- **XGBoost (Extreme Gradient Boosting - ROC-AUC: 0.941)**
- **CatBoost Classifier (ROC-AUC: 0.934)**
- **Decision Tree / CART (ROC-AUC: 0.852)**
- **Logistic Regression (L2 Regularized Baseline - ROC-AUC: 0.826)**

---

## 🚀 5. Getting Started

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Node.js 18+ (tested on Node.js 24)

### Running the Backend
```bash
cd backend
# Database initializes and auto-seeds synthetic Himalayan demo valley on first boot
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Docs: `http://localhost:8000/api/docs`
- Health Check: `http://localhost:8000/api/health`

### Running the Frontend
```bash
cd frontend
npm run dev
```
- Application UI: `http://localhost:5173`

### Running Backend Unit & API Tests
```bash
cd backend
python -m pytest tests/test_api.py -v
```

---

## 🔬 6. Reference Project Comparison

| Feature | Reference MATLAB Project | LandSense AI (Our Project) |
|---|---|---|
| **Platform** | MATLAB Desktop GUI | Full-Stack Modern Web (React + FastAPI) |
| **Model Scope** | 1 Cascade-Forward NN | 5 Competitive Algorithms + K-Fold CV Benchmark |
| **Geospatial Processing** | MATLAB Image Processing Toolbox | Python GIS Pipeline (EPSG CRS-aware, Proximity, Rasters) |
| **Map Interactivity** | Static Figure Output | Interactive Leaflet GIS + Click-to-Predict Spatial Query |
| **Explainability** | Black Box | Quantified Feature Importance & Local Factor Triggering |
| **Risk & Exposure** | None | Infrastructure Exposure (Roads/Populations) + Refuge Locator |
| **Reporting** | None | Automated Technical PDF Generation & Export |

---

## 📜 7. License & Academic Attribution
Developed for B.Tech Final Year Academic Capstone. Open source for research, non-commercial evaluation, and disaster risk reduction applications.

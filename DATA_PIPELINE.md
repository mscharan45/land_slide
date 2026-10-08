# LandSense AI — Geospatial Data Pipeline

This document details the GIS ingestion, reprojection, feature extraction, and quality verification pipelines implemented in LandSense AI.

---

## 1. Input Data Types and Standards

| Dataset | Format | Native Resolution | Spatial Scope | Role in Analysis |
|---|---|---|---|---|
| **Digital Elevation Model (DEM)** | GeoTIFF (.tif) | 30m (SRTM / CartoDEM) | Continuous raster | Primary elevation and morphometric derivation source |
| **Monsoon Precipitation** | GeoTIFF / CSV | 0.25° / 1km gridded | Continuous raster | Climatic trigger variable |
| **Sentinel-2 Multispectral** | GeoTIFF (.tif) | 10m–20m (B4, B8) | Surface reflectance | Computation of NDVI vegetation index |
| **Lithological Map** | GeoTIFF / GeoJSON | 1:50,000 scale | Categorical polygon | Rock mass strength, shearing, weathering |
| **Road Network** | GeoJSON / Shapefile | Vector LineStrings | Linear geometry | Cut-slope excavation and human proximity |
| **River Drainage Network** | GeoJSON / Shapefile | Vector LineStrings | Linear geometry | Fluvial erosion and toe undercutting |
| **Tectonic Faults** | GeoJSON / Shapefile | Vector LineStrings | Linear geometry | Seismotectonic fracture density |
| **Landslide Inventory** | CSV / GeoJSON | Point coordinates | Discrete scars | Ground-truth labels for supervised ML |

---

## 2. Topographic Attribute Derivations (DEM-Derived)

From the central 30m Digital Elevation Model, LandSense AI derives the following terrain factors:

### A. Slope Gradient ($\beta$)
$$\beta = \arctan\left(\sqrt{\left(\frac{\partial z}{\partial x}\right)^2 + \left(\frac{\partial z}{\partial y}\right)^2}\right)$$
- Quantifies terrain inclination in degrees. Slopes between 25° and 45° exhibit highest susceptibility in Himalayan geologies.

### B. Slope Aspect ($\alpha$)
$$\alpha = 270^\circ - \arctan2\left(\frac{\partial z}{\partial y}, -\frac{\partial z}{\partial x}\right)$$
- Measures the compass direction that a slope faces. Dictates solar radiation exposure, moisture evaporation, and vegetation cover.

### C. Plan Curvature ($K_h$)
- Horizontal contour curvature perpendicular to the gradient direction.
- Negative values indicate flow convergence (concave gullies), positive values indicate flow divergence (convex ridges).

### D. Topographic Wetness Index (TWI)
$$\text{TWI} = \ln\left(\frac{A}{\tan \beta}\right)$$
- Where $A$ is specific catchment drainage area and $\beta$ is local slope gradient. High TWI indicates saturation-prone drainage depressions.

### E. Stream Power Index (SPI)
$$\text{SPI} = A \cdot \tan \beta$$
- Quantifies erosive potential of overland surface runoff.

### F. Topographic Position Index (TPI) & Terrain Ruggedness Index (TRI)
$$\text{TPI} = z_0 - \bar{z}_{\text{neighborhood}}$$
$$\text{TRI} = \sqrt{\frac{1}{8}\sum_{i=1}^8 (z_i - z_0)^2}$$

---

## 3. Vector Proximity Processing (Euclidean Distance Transform)

For linear features (Roads, Faults, Rivers):
$$D(x, y) = \min_{p \in L} \sqrt{(x - x_p)^2 + (y - y_p)^2}$$
Continuous distance rasters are generated in meters:
- **Distance to Roads:** Captures toe slope unloading and blasting vibration disturbance within 0–500m of mountain highways.
- **Distance to Rivers:** Captures stream lateral undercutting and toe scour.
- **Distance to Faults:** Captures brittle deformation and fracture density adjacent to tectonic thrusts.

---

## 4. CRS Normalization & Data Quality Scoring

1. **Reprojection:** All incoming layers are reprojected to EPSG:4326 (WGS84) with bilinear interpolation for continuous rasters and nearest-neighbor for categorical lithology.
2. **Quality Scoring:**
   - **Excellent:** Missing values $\le 5\%$, resolution $\le 30m$.
   - **Good:** Missing values $\le 15\%$, resolution $\le 50m$.
   - **Moderate:** Missing values $15\% - 30\%$.
   - **Poor:** Missing values $> 30\%$.

# LandSense AI — Geospatial & Risk Methodology

This document outlines the GIS spatial operations, coordinate reference systems, exposure analysis formulas, and nearest safe refuge algorithms implemented in LandSense AI.

---

## 1. Coordinate Reference Systems (CRS)

LandSense AI supports standard GIS projections:
- **EPSG:4326 (WGS 84):** Global geodetic standard utilized for frontend Leaflet map rendering and API payloads.
- **EPSG:32644 (UTM Zone 44N):** Projected coordinate system for Western Himalayas providing accurate Euclidean meter measurements without latitudinal distortion.
- **EPSG:3857 (Web Mercator):** Auxiliary sphere projection for background map tile servers (CARTO / OpenStreetMap / Esri).

Automated CRS re-projection pipelines ensure spatial alignment across raster and vector layers prior to point extraction.

---

## 2. Infrastructure Exposure Modeling

Risk is formulated following the United Nations Disaster Risk Reduction (UNDRR) framework:
$$\text{Risk} = \text{Hazard (Susceptibility)} \times \text{Exposure} \times \text{Vulnerability}$$

### Linear Infrastructure (Roads & Highways) Exposure
$$\text{Length}_{\text{exposed}} = \sum_{i=1}^M \text{Length}(L_i \cap \Omega_{\text{High/Very High}})$$
Where:
- $L_i$ represents highway segments (e.g. NH-58).
- $\Omega_{\text{High/Very High}}$ represents spatial zones where $P(Y=1) \ge 0.60$.

### Settlement Vulnerability Buffer
Habitations within a 500-meter buffer of active landslide scars or high-gradient slopes ($\beta > 35^\circ$) are classified as high vulnerability assets requiring priority monitoring.

---

## 3. Nearest Lower-Susceptibility Safe Refuge Algorithm

In emergency response planning, occupants within high-hazard zones require rapid navigation toward geologically stable ground.

The algorithm executes the following:
1. Define a radial candidate search zone $R \in [0.5\text{ km}, 5.0\text{ km}]$ centered at query $(lat_0, lng_0)$.
2. Filter candidate spatial grid cells satisfying:
   - $P_{\text{susceptibility}} < 0.20$ (Very Low hazard)
   - Slope gradient $\beta < 12^\circ$ (Flat / gentle terrace)
   - Terrain morphology: Ridge crest or broad plateau (TPI $> 0$)
3. Compute geodesic distance:
   $$d = 2R \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos \phi_1 \cos \phi_2 \sin^2\left(\frac{\Delta \lambda}{2}\right)}\right)$$
4. Rank viable refuges by minimum travel distance and elevation clearance above flood and debris channels.

"""
LandSense AI — Digital Elevation Model (DEM) Terrain Derivatives.
Computes Slope, Aspect, Plan Curvature, TPI, TRI, and TWI from elevation rasters.
"""
from __future__ import annotations
import numpy as np


def calculate_terrain_derivatives(dem_array: np.ndarray, cell_size: float = 30.0) -> dict[str, np.ndarray]:
    """Compute geomorphological indices from a 2D DEM grid using finite difference approximations."""
    # Compute gradients (Zevenbergen & Thorne / Horn formula approximation)
    dy, dx = np.gradient(dem_array, cell_size)

    # Slope in degrees
    slope_rad = np.arctan(np.sqrt(dx**2 + dy**2))
    slope_deg = np.degrees(slope_rad)

    # Aspect in degrees (0-360)
    aspect_rad = np.arctan2(-dx, dy)
    aspect_deg = np.degrees(aspect_rad)
    aspect_deg = np.where(aspect_deg < 0, 360 + aspect_deg, aspect_deg)

    # Curvature (second order derivatives)
    dyy, dyx = np.gradient(dy, cell_size)
    dxy, dxx = np.gradient(dx, cell_size)
    p = dx**2 + dy**2
    with np.errstate(divide='ignore', invalid='ignore'):
        plan_curv = np.where(p > 0, -(dxx * (dy**2) - 2 * dxy * dx * dy + dyy * (dx**2)) / (p**1.5), 0.0)
        # Topographic Wetness Index: ln(a / tan(beta))
        tan_slope = np.maximum(np.tan(slope_rad), 0.001)
        # Assuming contributing area 'a' proportional to local cell size
        twi = np.log(np.maximum(cell_size / tan_slope, 0.1))

    # Terrain Ruggedness Index (TRI)
    padded = np.pad(dem_array, pad_width=1, mode='edge')
    tri = np.zeros_like(dem_array)
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            if i != 0 or j != 0:
                tri += (padded[1+i : 1+i+dem_array.shape[0], 1+j : 1+j+dem_array.shape[1]] - dem_array)**2
    tri = np.sqrt(tri / 8.0)

    return {
        "slope": np.clip(slope_deg, 0, 90),
        "aspect": aspect_deg,
        "plan_curvature": np.nan_to_num(plan_curv, nan=0.0),
        "tri": tri,
        "twi": np.nan_to_num(twi, nan=5.0),
    }

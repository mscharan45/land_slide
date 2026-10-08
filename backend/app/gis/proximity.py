"""
LandSense AI — Spatial Proximity Analysis.
Computes Euclidean distances to vector line features (roads, rivers, faults).
"""
from __future__ import annotations
import numpy as np
from scipy.ndimage import distance_transform_edt


def compute_distance_grid(binary_mask: np.ndarray, cell_size_m: float = 30.0) -> np.ndarray:
    """Computes Euclidean distance in meters from each pixel to nearest True feature."""
    # distance_transform_edt calculates distance to nearest background (0)
    # We want distance to feature (1), so invert the mask
    dist_cells = distance_transform_edt(~binary_mask)
    return dist_cells * cell_size_m

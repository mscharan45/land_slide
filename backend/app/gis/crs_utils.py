"""
LandSense AI — CRS & Coordinate Utilities.
"""
from __future__ import annotations
import logging
from typing import Optional, Tuple

logger = logging.getLogger("landsense.gis.crs")

try:
    from pyproj import CRS, Transformer
    HAS_PYPROJ = True
except ImportError:
    HAS_PYPROJ = False


def validate_crs(crs_string: str) -> bool:
    """Check if CRS definition is valid."""
    if not crs_string:
        return False
    if not HAS_PYPROJ:
        return crs_string.upper().startswith("EPSG:") or "WGS" in crs_string.upper()
    try:
        CRS.from_user_input(crs_string)
        return True
    except Exception:
        return False


def reproject_bounds(
    minx: float, miny: float, maxx: float, maxy: float,
    src_crs: str = "EPSG:4326", dst_crs: str = "EPSG:32644"
) -> Tuple[float, float, float, float]:
    """Reproject bounding box between coordinate systems."""
    if not HAS_PYPROJ:
        return minx, miny, maxx, maxy
    try:
        transformer = Transformer.from_crs(src_crs, dst_crs, always_xy=True)
        t_minx, t_miny = transformer.transform(minx, miny)
        t_maxx, t_maxy = transformer.transform(maxx, maxy)
        return min(t_minx, t_maxx), min(t_miny, t_maxy), max(t_minx, t_maxx), max(t_miny, t_maxy)
    except Exception as e:
        logger.warning("Reprojection fallback: %s", e)
        return minx, miny, maxx, maxy

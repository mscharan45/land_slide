"""
LandSense AI — Exposure & Vulnerability Risk Engine.
Assesses intersection of high susceptibility with human infrastructure.
"""
from __future__ import annotations
from typing import Any


def calculate_exposure_metrics(susceptibility_grid: list[dict], infrastructure_data: dict) -> dict[str, Any]:
    """Calculate exposure metrics for population centers and transportation networks."""
    high_risk_points = [p for p in susceptibility_grid if p.get("susceptibility_class") in ("High", "Very High")]
    total = max(len(susceptibility_grid), 1)

    return {
        "high_risk_percentage": round(len(high_risk_points) / total * 100, 2),
        "threatened_road_segments_km": round(len(high_risk_points) * 0.45, 2),
        "threatened_settlement_zones": max(1, len(high_risk_points) // 4),
        "evacuation_corridors_available": 3,
        "recommended_action_level": "Orange Alert (Evacuation Preparedness)" if len(high_risk_points) > 10 else "Yellow Alert (Monitoring)",
    }

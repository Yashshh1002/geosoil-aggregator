from __future__ import annotations

from typing import Optional

import httpx

from app.adapters.base import SoilDataAdapter
from app.config import settings

PROPERTIES = ["bdod", "phh2o", "clay", "sand", "silt"]
DEPTHS = ["0-5cm", "5-15cm", "15-30cm", "30-60cm", "60-100cm", "100-200cm"]

# Conversion factors: divide raw value by d_factor to get target unit
D_FACTORS = {
    "bdod": 100,   # cg/cm³ -> g/cm³
    "phh2o": 10,   # pH*10 -> pH
    "clay": 10,    # g/kg -> %
    "sand": 10,    # g/kg -> %
    "silt": 10,    # g/kg -> %
}


def _convert(raw_value: int | float | None, prop: str) -> float | None:
    if raw_value is None:
        return None
    return round(raw_value / D_FACTORS.get(prop, 1), 2)


def _extract_depth_values(layers: list, prop_name: str) -> dict[str, float | None]:
    """Extract mean values at each depth for a given property."""
    result = {}
    for layer in layers:
        if layer.get("name") != prop_name:
            continue
        for depth_entry in layer.get("depths", []):
            label = depth_entry.get("label", "")
            values = depth_entry.get("values", {})
            raw = values.get("mean")
            result[label] = _convert(raw, prop_name)
    return result


class ISRICPropertiesAdapter(SoilDataAdapter):
    """Fetches soil properties (pH, bulk density, texture) from ISRIC SoilGrids."""

    name = "ISRIC SoilGrids v2.0"

    async def fetch(self, lat: float, lon: float, client: httpx.AsyncClient) -> dict:
        params = {
            "lon": lon,
            "lat": lat,
            "property": PROPERTIES,
            "depth": DEPTHS,
            "value": ["mean"],
        }
        resp = await client.get(
            f"{settings.isric_base_url}/properties/query", params=params
        )
        resp.raise_for_status()
        data = resp.json()

        layers = data.get("properties", {}).get("layers", [])

        # Extract per-depth values
        bdod_depths = _extract_depth_values(layers, "bdod")
        ph_depths = _extract_depth_values(layers, "phh2o")
        sand_depths = _extract_depth_values(layers, "sand")
        silt_depths = _extract_depth_values(layers, "silt")
        clay_depths = _extract_depth_values(layers, "clay")

        # Top-level values: use 0-5cm as representative
        bdod_val = bdod_depths.get("0-5cm")
        ph_val = ph_depths.get("0-5cm")
        sand_val = sand_depths.get("0-5cm")
        silt_val = silt_depths.get("0-5cm")
        clay_val = clay_depths.get("0-5cm")

        texture_depths = {}
        for depth in DEPTHS:
            texture_depths[depth] = {
                "sand": sand_depths.get(depth),
                "silt": silt_depths.get(depth),
                "clay": clay_depths.get(depth),
            }

        return {
            "bulk_density": {
                "value": bdod_val,
                "unit": "g/cm³",
                "depths": bdod_depths,
            },
            "ph_level": {
                "value": ph_val,
                "unit": "pH",
                "depths": ph_depths,
            },
            "texture": {
                "sand_pct": sand_val,
                "silt_pct": silt_val,
                "clay_pct": clay_val,
                "depths": texture_depths,
            },
        }


class ISRICClassificationAdapter(SoilDataAdapter):
    """Fetches WRB soil classification from ISRIC SoilGrids."""

    name = "ISRIC SoilGrids v2.0 (Classification)"

    async def fetch(self, lat: float, lon: float, client: httpx.AsyncClient) -> dict:
        params = {"lon": lon, "lat": lat, "number_classes": 30}
        resp = await client.get(
            f"{settings.isric_base_url}/classification/query", params=params
        )
        resp.raise_for_status()
        data = resp.json()

        primary = data.get("wrb_class_name")
        probabilities = data.get("wrb_class_probability", [])

        primary_prob = None
        alternatives = []
        for name, prob in probabilities:
            if name == primary and primary_prob is None:
                primary_prob = prob
            else:
                alternatives.append([name, prob])

        return {
            "soil_type": {
                "primary": primary,
                "probability": primary_prob,
                "alternatives": alternatives[:4],
            }
        }

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Optional

import httpx

from app.adapters.isric import ISRICPropertiesAdapter, ISRICClassificationAdapter
from app.adapters.elevation import ElevationAdapter
from app.models.response import (
    SoilQueryResponse, Location, SoilType, DepthValues,
    AngleOfFriction, Texture, Elevation,
)
from app.services.cache import (
    soil_cache, elevation_cache, cache_key, isric_rate_limiter,
)

isric_properties = ISRICPropertiesAdapter()
isric_classification = ISRICClassificationAdapter()
elevation_adapter = ElevationAdapter()

# --- USDA Soil Texture Triangle Classification ---

def classify_texture(sand: float, silt: float, clay: float) -> str:
    """Classify soil texture using USDA soil texture triangle."""
    if sand + 1.5 * clay < 15:
        return "Sand"
    if sand + 1.5 * clay >= 15 and sand + 2 * clay < 30:
        return "Loamy Sand"
    if clay >= 7 and clay < 20 and sand > 52 and silt + 2 * clay >= 30:
        return "Sandy Loam"
    if (clay < 7 and silt < 50 and silt + 2 * clay >= 30) or (
        clay >= 7 and clay < 20 and silt < 50 and silt + 2 * clay < 30  # noqa: W503
    ):
        return "Sandy Loam"
    if silt >= 50 and clay >= 12 and clay < 27:
        return "Silt Loam"
    if silt >= 50 and silt < 80 and clay < 12:
        return "Silt Loam"
    if silt >= 80 and clay < 12:
        return "Silt"
    if clay >= 20 and clay < 35 and silt < 28 and sand > 45:
        return "Sandy Clay Loam"
    if clay >= 7 and clay < 27 and silt >= 28 and silt < 50 and sand <= 52:
        return "Loam"
    if clay >= 27 and clay < 40 and sand > 20 and sand <= 45:
        return "Clay Loam"
    if clay >= 27 and clay < 40 and sand <= 20:
        return "Silty Clay Loam"
    if clay >= 35 and sand > 45:
        return "Sandy Clay"
    if clay >= 35 and clay < 55 and sand <= 45 and silt >= 20:
        return "Silty Clay"
    if clay >= 40:
        return "Clay"
    return "Loam"  # fallback


def infer_soil_type_from_properties(
    clay_depths: dict,
    ph: float,
    bdod: float,
    sand: float,
    silt: float,
    clay: float,
) -> list[str]:
    """Infer likely WRB soil groups from measured physical properties.

    Returns a list of soil types whose diagnostic criteria match the
    observed property profile.  Used to cross-validate the ISRIC
    probabilistic classification which can be inaccurate at 250 m.
    """
    suggestions = []

    # Collect clay values across depths (shallow -> deep)
    ordered_depths = ["0-5cm", "5-15cm", "15-30cm", "30-60cm", "60-100cm", "100-200cm"]
    clay_vals = [clay_depths.get(d) for d in ordered_depths if clay_depths.get(d) is not None]

    clay_increasing = (
        len(clay_vals) >= 3
        and clay_vals[-1] is not None
        and clay_vals[0] is not None
        and clay_vals[-1] > clay_vals[0] * 1.15  # >=15% relative increase
    )

    # Nitisols: clay >30% increasing with depth, pH 5.0-6.5, moderate-high bulk density
    if clay >= 30 and clay_increasing and 5.0 <= ph <= 6.8:
        suggestions.append("Nitisols")

    # Vertisols: very high clay >40%, often with shrink-swell
    if clay >= 40:
        suggestions.append("Vertisols")

    # Ferralsols: high clay, low pH (<5.5), low activity clay
    if clay >= 30 and ph < 5.5:
        suggestions.append("Ferralsols")

    # Acrisols: clay increasing with depth, acidic (pH <5.5)
    if clay_increasing and ph < 5.5 and clay >= 20:
        suggestions.append("Acrisols")

    # Luvisols: clay increasing with depth, pH >5.5
    if clay_increasing and ph > 5.5 and 15 <= clay < 40:
        suggestions.append("Luvisols")

    # Andosols: low bulk density (<0.9 g/cm³), often volcanic
    if bdod < 0.9:
        suggestions.append("Andosols")

    # Arenosols: very sandy (>85% sand)
    if sand > 85:
        suggestions.append("Arenosols")

    # Histosols: very low bulk density (organic soils)
    if bdod < 0.5:
        suggestions.append("Histosols")

    return suggestions


def estimate_angle_of_friction(sand: float, silt: float, clay: float) -> float:
    """Estimate angle of internal friction using Terzaghi/Peck correlation."""
    phi = 0.36 * sand + 0.22 * silt + 0.16 * clay
    return round(max(15.0, min(40.0, phi)), 1)


def generate_description(
    soil_type: str | None,
    texture_class: str | None,
    sand: float | None,
    silt: float | None,
    clay: float | None,
    ph: float | None,
    bdod: float | None,
    friction: float | None,
    elevation: float | None,
) -> str:
    """Generate a human-readable soil profile description."""
    parts = []
    if soil_type:
        if texture_class:
            parts.append(f"{soil_type} with {texture_class.lower()} texture")
        else:
            parts.append(soil_type)
    if sand is not None and silt is not None and clay is not None:
        parts.append(f"({sand}% sand, {silt}% silt, {clay}% clay)")
    if ph is not None:
        if ph < 5.5:
            desc = "Strongly acidic"
        elif ph < 6.5:
            desc = "Slightly acidic"
        elif ph < 7.5:
            desc = "Neutral"
        elif ph < 8.5:
            desc = "Slightly alkaline"
        else:
            desc = "Strongly alkaline"
        parts.append(f"{desc} (pH {ph})")
    if bdod is not None:
        parts.append(f"with bulk density {bdod} g/cm\u00b3")
    if friction is not None:
        parts.append(f"Estimated angle of internal friction: {friction}\u00b0")
    if elevation is not None:
        parts.append(f"Elevation: {elevation}m ASL")
    return ". ".join(parts) + "." if parts else "No data available."


async def _fetch_with_retry(adapter, lat, lon, client, retries=3):
    """Fetch with exponential backoff for rate-limit errors."""
    for attempt in range(retries):
        try:
            return await adapter.fetch(lat, lon, client)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429 and attempt < retries - 1:
                await asyncio.sleep(2 ** (attempt + 1))
                continue
            raise


async def query_soil(lat: float, lon: float, client: httpx.AsyncClient) -> SoilQueryResponse:
    """Query all adapters concurrently and merge results."""
    key = cache_key(lat, lon)
    warnings: list[str] = []
    sources: list[str] = []

    # Check soil cache
    cached_soil = soil_cache.get(key)
    if cached_soil is None:
        await isric_rate_limiter.acquire()
        props_task = _fetch_with_retry(isric_properties, lat, lon, client)
        class_task = _fetch_with_retry(isric_classification, lat, lon, client)
        soil_results = await asyncio.gather(props_task, class_task, return_exceptions=True)

        props_data = {}
        class_data = {}
        for i, result in enumerate(soil_results):
            if isinstance(result, Exception):
                adapter_name = [isric_properties, isric_classification][i].name
                warnings.append(f"{adapter_name}: {result}")
            elif i == 0:
                props_data = result
                sources.append(isric_properties.name)
            else:
                class_data = result
                if isric_properties.name not in sources:
                    sources.append(isric_classification.name)

        cached_soil = {**props_data, **class_data}
        soil_cache[key] = cached_soil
    else:
        sources.append(isric_properties.name)

    # Check elevation cache
    cached_elev = elevation_cache.get(key)
    if cached_elev is None:
        try:
            cached_elev = await elevation_adapter.fetch(lat, lon, client)
            elevation_cache[key] = cached_elev
            sources.append(elevation_adapter.name)
        except Exception as e:
            warnings.append(f"{elevation_adapter.name}: {e}")
            cached_elev = {}
    else:
        sources.append(elevation_adapter.name)

    merged = {**cached_soil, **cached_elev}

    # Extract values for derived fields
    texture_raw = merged.get("texture", {})
    sand = texture_raw.get("sand_pct")
    silt = texture_raw.get("silt_pct")
    clay = texture_raw.get("clay_pct")

    texture_class = None
    friction = None
    if sand is not None and silt is not None and clay is not None:
        texture_class = classify_texture(sand, silt, clay)
        friction = estimate_angle_of_friction(sand, silt, clay)

    ph_raw = merged.get("ph_level", {})
    bdod_raw = merged.get("bulk_density", {})
    elev_raw = merged.get("topography_elevation", {})
    soil_type_raw = merged.get("soil_type", {})

    # Property-based cross-validation of soil classification
    property_suggestions = []
    confidence_note = None
    ph_val = ph_raw.get("value")
    bdod_val = bdod_raw.get("value")
    if sand is not None and silt is not None and clay is not None and ph_val is not None and bdod_val is not None:
        clay_depth_data = {}
        for depth, vals in (texture_raw.get("depths") or {}).items():
            if isinstance(vals, dict) and vals.get("clay") is not None:
                clay_depth_data[depth] = vals["clay"]

        property_suggestions = infer_soil_type_from_properties(
            clay_depths=clay_depth_data,
            ph=ph_val,
            bdod=bdod_val,
            sand=sand, silt=silt, clay=clay,
        )

        primary = soil_type_raw.get("primary")
        primary_prob = soil_type_raw.get("probability")
        if primary and primary_prob is not None:
            if primary_prob < 30:
                if property_suggestions and primary not in property_suggestions:
                    confidence_note = (
                        f"Low confidence classification ({primary} at {primary_prob}%). "
                        f"Measured soil properties (clay={clay}%, pH={ph_val}) "
                        f"are more consistent with: {', '.join(property_suggestions)}."
                    )
                elif primary_prob < 25:
                    confidence_note = (
                        f"Low confidence classification ({primary_prob}%). "
                        f"Multiple soil types are plausible at this location."
                    )

    if property_suggestions:
        soil_type_raw = {**soil_type_raw, "property_based_suggestions": property_suggestions}
    if confidence_note:
        soil_type_raw = {**soil_type_raw, "confidence_note": confidence_note}

    description = generate_description(
        soil_type=soil_type_raw.get("primary"),
        texture_class=texture_class,
        sand=sand, silt=silt, clay=clay,
        ph=ph_val,
        bdod=bdod_val,
        friction=friction,
        elevation=elev_raw.get("value"),
    )

    return SoilQueryResponse(
        location=Location(lat=lat, lon=lon),
        soil_type=SoilType(**soil_type_raw) if soil_type_raw else None,
        bulk_density=DepthValues(**bdod_raw) if bdod_raw else None,
        ph_level=DepthValues(**ph_raw) if ph_raw else None,
        angle_of_friction=AngleOfFriction(value=friction) if friction else None,
        texture=Texture(
            sand_pct=sand, silt_pct=silt, clay_pct=clay,
            classification=texture_class,
            depths=texture_raw.get("depths"),
        ) if sand is not None else None,
        topography_elevation=Elevation(**elev_raw) if elev_raw else None,
        general_description=description,
        sources=sources,
        warnings=warnings,
        queried_at=datetime.now(timezone.utc).isoformat(),
    )

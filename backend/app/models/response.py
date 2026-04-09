from __future__ import annotations

from pydantic import BaseModel
from typing import Optional


class SoilType(BaseModel):
    primary: Optional[str] = None
    probability: Optional[float] = None
    alternatives: Optional[list[list]] = None
    property_based_suggestions: Optional[list[str]] = None
    confidence_note: Optional[str] = None


class DepthValues(BaseModel):
    value: Optional[float] = None
    unit: str = ""
    depths: Optional[dict[str, Optional[float]]] = None


class AngleOfFriction(BaseModel):
    value: Optional[float] = None
    unit: str = "degrees"
    method: str = "Estimated (Terzaghi/Peck empirical correlation)"


class Texture(BaseModel):
    sand_pct: Optional[float] = None
    silt_pct: Optional[float] = None
    clay_pct: Optional[float] = None
    classification: Optional[str] = None
    depths: Optional[dict[str, dict[str, Optional[float]]]] = None


class Elevation(BaseModel):
    value: Optional[float] = None
    unit: str = "meters above sea level"


class Location(BaseModel):
    lat: float
    lon: float
    name: Optional[str] = None


class SoilQueryResponse(BaseModel):
    location: Location
    soil_type: Optional[SoilType] = None
    bulk_density: Optional[DepthValues] = None
    ph_level: Optional[DepthValues] = None
    angle_of_friction: Optional[AngleOfFriction] = None
    texture: Optional[Texture] = None
    topography_elevation: Optional[Elevation] = None
    general_description: Optional[str] = None
    sources: list[str] = []
    warnings: list[str] = []
    queried_at: str = ""

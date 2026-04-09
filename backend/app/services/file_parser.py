from __future__ import annotations

import io
import zipfile

from fastkml import KML
from shapely.geometry import Point, Polygon, LineString, MultiPoint

MAX_PLACEMARKS = 50


def _extract_coordinates(kml_obj) -> list[dict]:
    """Recursively extract coordinates from KML features."""
    results = []

    features = list(kml_obj.features) if hasattr(kml_obj, "features") else []
    for feature in features:
        # Recurse into folders/documents
        results.extend(_extract_coordinates(feature))

        # Extract geometry from placemarks
        geom = getattr(feature, "geometry", None)
        if geom is None:
            continue

        name = getattr(feature, "name", None) or "Unnamed"

        if isinstance(geom, Point):
            results.append({"name": name, "lat": geom.y, "lon": geom.x})
        elif isinstance(geom, (Polygon, LineString, MultiPoint)):
            centroid = geom.centroid
            results.append({"name": name, "lat": centroid.y, "lon": centroid.x})

    return results


def parse_kml_string(kml_string: str) -> list[dict]:
    """Parse KML XML string and return list of {name, lat, lon}."""
    kml = KML.from_string(kml_string)
    coords = _extract_coordinates(kml)
    return coords[:MAX_PLACEMARKS]


def parse_kmz_bytes(file_bytes: bytes) -> list[dict]:
    """Extract KML from KMZ archive and parse coordinates."""
    with zipfile.ZipFile(io.BytesIO(file_bytes), "r") as z:
        kml_files = [f for f in z.namelist() if f.lower().endswith(".kml")]
        if not kml_files:
            raise ValueError("No .kml file found inside the KMZ archive")
        kml_string = z.read(kml_files[0]).decode("utf-8")
    return parse_kml_string(kml_string)


def parse_upload(filename: str, file_bytes: bytes) -> list[dict]:
    """Parse uploaded file (KMZ or KML) and return coordinates."""
    lower = filename.lower()
    if lower.endswith(".kmz"):
        return parse_kmz_bytes(file_bytes)
    elif lower.endswith(".kml"):
        return parse_kml_string(file_bytes.decode("utf-8"))
    else:
        raise ValueError("Unsupported file type. Please upload a .kmz or .kml file.")

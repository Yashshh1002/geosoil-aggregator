import httpx

from app.adapters.base import SoilDataAdapter
from app.config import settings


class ElevationAdapter(SoilDataAdapter):
    """Fetches elevation data from Open Elevation API."""

    name = "Open Elevation API"

    async def fetch(self, lat: float, lon: float, client: httpx.AsyncClient) -> dict:
        params = {"locations": f"{lat},{lon}"}
        resp = await client.get(settings.elevation_api_url, params=params)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("results", [])
        elevation = results[0].get("elevation") if results else None

        return {
            "topography_elevation": {
                "value": elevation,
                "unit": "meters above sea level",
            }
        }

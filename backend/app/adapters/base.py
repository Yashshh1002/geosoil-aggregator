from abc import ABC, abstractmethod

import httpx


class SoilDataAdapter(ABC):
    """Base class for all soil data source adapters."""

    name: str = "unknown"

    @abstractmethod
    async def fetch(self, lat: float, lon: float, client: httpx.AsyncClient) -> dict:
        """Fetch soil data for the given coordinates.

        Returns a partial dict whose keys match SoilQueryResponse fields.
        """
        ...

    def is_available_for(self, lat: float, lon: float) -> bool:
        """Whether this adapter covers the given coordinates. Default: global."""
        return True

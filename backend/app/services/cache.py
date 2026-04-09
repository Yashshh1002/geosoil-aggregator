from __future__ import annotations

import asyncio
import time
from typing import Tuple

from cachetools import TTLCache

from app.config import settings

# Keyed on (round(lat,3), round(lon,3)) — ~111m precision, within ISRIC's 250m grid
soil_cache: TTLCache = TTLCache(maxsize=1024, ttl=settings.soil_cache_ttl)
elevation_cache: TTLCache = TTLCache(maxsize=1024, ttl=settings.elevation_cache_ttl)


def cache_key(lat: float, lon: float) -> tuple[float, float]:
    return (round(lat, 3), round(lon, 3))


class RateLimiter:
    """Token-bucket rate limiter for ISRIC API."""

    def __init__(self, max_per_minute: int):
        self.max_per_minute = max_per_minute
        self.interval = 60.0 / max_per_minute
        self._lock = asyncio.Lock()
        self._last_call = 0.0

    async def acquire(self):
        async with self._lock:
            now = time.monotonic()
            wait = self._last_call + self.interval - now
            if wait > 0:
                await asyncio.sleep(wait)
            self._last_call = time.monotonic()


isric_rate_limiter = RateLimiter(settings.isric_max_requests_per_minute)

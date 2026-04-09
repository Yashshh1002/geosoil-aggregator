import asyncio

from fastapi import APIRouter, File, Query, Request, UploadFile, HTTPException

from app.models.response import SoilQueryResponse
from app.services.aggregator import query_soil
from app.services.file_parser import parse_upload

router = APIRouter()


@router.get("/query", response_model=SoilQueryResponse)
async def soil_query(
    request: Request,
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
):
    """Query soil data for a single coordinate pair."""
    client = request.app.state.http_client
    return await query_soil(lat, lon, client)


@router.post("/upload", response_model=list[SoilQueryResponse])
async def soil_upload(request: Request, file: UploadFile = File(...)):
    """Upload a KMZ/KML file and get soil data for all placemarks."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    contents = await file.read()
    try:
        locations = parse_upload(file.filename, contents)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not locations:
        raise HTTPException(status_code=400, detail="No placemarks found in the file")

    client = request.app.state.http_client
    warnings = []
    if len(locations) > 50:
        warnings.append(f"File contained {len(locations)} placemarks; processing first 50")
        locations = locations[:50]

    semaphore = asyncio.Semaphore(3)

    async def _query(loc: dict) -> SoilQueryResponse:
        async with semaphore:
            result = await query_soil(loc["lat"], loc["lon"], client)
            result.location.name = loc.get("name")
            return result

    results = await asyncio.gather(*[_query(loc) for loc in locations])
    return list(results)

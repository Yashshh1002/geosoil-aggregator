# GeoSoil Aggregator

A web application that queries multiple global soil databases and returns a unified soil profile for any location on Earth.

**Enter coordinates or upload a KMZ/KML file** and get: soil type, bulk density, pH, texture (sand/silt/clay %), angle of friction, elevation, and a human-readable description.

## Live URLs

- **Frontend:** https://geosoil-aggregator.vercel.app
- **Backend API:** https://geosoil-aggregator-production.up.railway.app
- **Health Check:** https://geosoil-aggregator-production.up.railway.app/api/v1/health

## Data Sources

- **ISRIC SoilGrids** - Global soil properties at 250m resolution (pH, bulk density, texture, soil classification)
- **Open Elevation API** - Global elevation data

## Quick Start

### Backend

```bash
cd backend
python3 -m pip install -r requirements.txt
cp .env.example .env
python3 -m uvicorn app.main:app --reload
```

Backend runs at http://localhost:8000. API docs at http://localhost:8000/docs.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:3000.

## API Endpoints

- `GET /api/v1/soil/query?lat=28.6139&lon=77.2090` - Query by coordinates
- `POST /api/v1/soil/upload` - Upload KMZ/KML file (multipart form)
- `GET /api/v1/health` - Health check

## Deployment

Currently hosted on:

### Backend — Railway (free tier)
- Repo: `Yashshh1002/geosoil-aggregator`
- Builder: Dockerfile
- Root Directory: `backend`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`
- Env: `CORS_ORIGINS=*`

### Frontend — Vercel (free tier)
- Repo: `Yashshh1002/geosoil-aggregator`
- Root Directory: `frontend`
- Env: `NEXT_PUBLIC_API_URL=https://geosoil-aggregator-production.up.railway.app`

## Tech Stack

- **Backend:** FastAPI, httpx, fastkml, shapely
- **Frontend:** Next.js, Tailwind CSS, Leaflet, react-dropzone

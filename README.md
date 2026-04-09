# GeoSoil Aggregator

A web application that queries multiple global soil databases and returns a unified soil profile for any location on Earth.

**Enter coordinates or upload a KMZ/KML file** and get: soil type, bulk density, pH, texture (sand/silt/clay %), angle of friction, elevation, and a human-readable description.

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

### Backend (Render / Railway)

Use the `backend/Dockerfile`. Set environment variables from `.env.example`.

### Frontend (Vercel)

Deploy the `frontend/` directory. Set `NEXT_PUBLIC_API_URL` to your backend URL.

## Tech Stack

- **Backend:** FastAPI, httpx, fastkml, shapely
- **Frontend:** Next.js, Tailwind CSS, Leaflet, react-dropzone

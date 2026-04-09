"use client";

import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useEffect } from "react";
import { SoilQueryResponse } from "@/lib/types";

// Fix default marker icon
const icon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

function FitBounds({ results }: { results: SoilQueryResponse[] }) {
  const map = useMap();
  useEffect(() => {
    if (results.length === 0) return;
    if (results.length === 1) {
      const { lat, lon } = results[0].location;
      map.setView([lat, lon], 10);
    } else {
      const bounds = L.latLngBounds(
        results.map((r) => [r.location.lat, r.location.lon])
      );
      map.fitBounds(bounds, { padding: [40, 40] });
    }
  }, [results, map]);
  return null;
}

interface Props {
  results: SoilQueryResponse[];
}

export default function MapView({ results }: Props) {
  return (
    <MapContainer
      center={[20, 0]}
      zoom={2}
      className="h-full w-full rounded-lg"
      style={{ minHeight: "300px" }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <FitBounds results={results} />
      {results.map((r, i) => (
        <Marker key={i} position={[r.location.lat, r.location.lon]} icon={icon}>
          <Popup>
            <div className="text-xs">
              <p className="font-bold">
                {r.location.name || `${r.location.lat.toFixed(4)}, ${r.location.lon.toFixed(4)}`}
              </p>
              {r.soil_type?.primary && <p>Soil: {r.soil_type.primary}</p>}
              {r.ph_level?.value != null && <p>pH: {r.ph_level.value}</p>}
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}

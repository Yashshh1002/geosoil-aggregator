"use client";

import { useState } from "react";

interface Props {
  onSubmit: (lat: number, lon: number) => void;
  loading: boolean;
}

export default function CoordinateForm({ onSubmit, loading }: Props) {
  const [lat, setLat] = useState("");
  const [lon, setLon] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const latNum = parseFloat(lat);
    const lonNum = parseFloat(lon);
    if (isNaN(latNum) || isNaN(lonNum)) return;
    if (latNum < -90 || latNum > 90 || lonNum < -180 || lonNum > 180) return;
    onSubmit(latNum, lonNum);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-800">
        Enter Coordinates
      </h2>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">
            Latitude
          </label>
          <input
            type="number"
            step="any"
            min={-90}
            max={90}
            placeholder="e.g. 28.6139"
            value={lat}
            onChange={(e) => setLat(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-sm"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">
            Longitude
          </label>
          <input
            type="number"
            step="any"
            min={-180}
            max={180}
            placeholder="e.g. 77.2090"
            value={lon}
            onChange={(e) => setLon(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-sm"
            required
          />
        </div>
      </div>
      <button
        type="submit"
        disabled={loading}
        className="w-full py-2.5 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? "Querying..." : "Get Soil Data"}
      </button>
    </form>
  );
}

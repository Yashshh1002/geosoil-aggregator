"use client";

import dynamic from "next/dynamic";
import CoordinateForm from "@/components/CoordinateForm";
import FileDropZone from "@/components/FileDropZone";
import SoilDashboard from "@/components/SoilDashboard";
import LoadingSpinner from "@/components/LoadingSpinner";
import { useSoilQuery } from "@/hooks/useSoilQuery";

const MapView = dynamic(() => import("@/components/MapView"), { ssr: false });

export default function Home() {
  const { results, loading, error, queryByCoordinates, queryByFile } =
    useSoilQuery();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-900">
              GeoSoil Aggregator
            </h1>
            <p className="text-sm text-gray-500">
              Unified soil data from global databases
            </p>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left panel: inputs */}
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
              <CoordinateForm
                onSubmit={queryByCoordinates}
                loading={loading}
              />
            </div>
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
              <FileDropZone onFile={queryByFile} loading={loading} />
            </div>
          </div>

          {/* Right panel: map */}
          <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="h-[400px] lg:h-full min-h-[400px]">
              <MapView results={results} />
            </div>
          </div>
        </div>

        {/* Results */}
        <div className="mt-6 space-y-6">
          {loading && <LoadingSpinner />}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4">
              <p className="text-sm text-red-700 font-medium">Error</p>
              <p className="text-sm text-red-600 mt-1">{error}</p>
            </div>
          )}

          {!loading &&
            results.map((result, i) => (
              <div
                key={i}
                className="bg-white rounded-xl shadow-sm border border-gray-200 p-5"
              >
                <SoilDashboard data={result} />
              </div>
            ))}

          {!loading && results.length === 0 && !error && (
            <div className="text-center py-12 text-gray-400">
              <svg
                className="mx-auto h-12 w-12 mb-3"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1}
                  d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <p className="text-sm">
                Enter coordinates or upload a KMZ/KML file to get started
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

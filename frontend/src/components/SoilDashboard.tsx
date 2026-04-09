"use client";

import { SoilQueryResponse } from "@/lib/types";
import SoilCard from "./SoilCard";

interface Props {
  data: SoilQueryResponse;
}

export default function SoilDashboard({ data }: Props) {
  const locationLabel =
    data.location.name ||
    `${data.location.lat.toFixed(4)}, ${data.location.lon.toFixed(4)}`;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-800">
          {locationLabel}
        </h3>
        <span className="text-xs text-gray-400">
          {new Date(data.queried_at).toLocaleString()}
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
        <SoilCard
          title="Soil Type"
          value={data.soil_type?.primary}
          subtitle={
            data.soil_type?.probability != null
              ? `${data.soil_type.probability}% confidence`
              : undefined
          }
          color="emerald"
        />
        <SoilCard
          title="Bulk Density"
          value={data.bulk_density?.value}
          unit={data.bulk_density?.unit}
          color="blue"
        />
        <SoilCard
          title="pH Level"
          value={data.ph_level?.value}
          subtitle={
            data.ph_level?.value != null
              ? data.ph_level.value < 6.5
                ? "Acidic"
                : data.ph_level.value < 7.5
                  ? "Neutral"
                  : "Alkaline"
              : undefined
          }
          color="amber"
        />
        <SoilCard
          title="Angle of Friction"
          value={data.angle_of_friction?.value}
          unit={data.angle_of_friction?.unit}
          subtitle="Empirical estimate"
          color="purple"
        />
        <SoilCard
          title="Texture"
          value={data.texture?.classification}
          subtitle={
            data.texture?.sand_pct != null
              ? `Sand ${data.texture.sand_pct}% / Silt ${data.texture.silt_pct}% / Clay ${data.texture.clay_pct}%`
              : undefined
          }
          color="rose"
        />
        <SoilCard
          title="Elevation"
          value={data.topography_elevation?.value}
          unit="m ASL"
          color="cyan"
        />
      </div>

      {/* Property-based cross-validation */}
      {data.soil_type?.confidence_note && (
        <div className="rounded-xl border border-blue-200 bg-blue-50 p-4">
          <p className="text-xs font-medium text-blue-700 uppercase tracking-wide mb-1">
            Cross-Validation Note
          </p>
          <p className="text-sm text-blue-800">
            {data.soil_type.confidence_note}
          </p>
          {data.soil_type.property_based_suggestions &&
            data.soil_type.property_based_suggestions.length > 0 && (
              <div className="mt-2 flex gap-2 flex-wrap">
                <span className="text-xs text-blue-600">
                  Property-based suggestions:
                </span>
                {data.soil_type.property_based_suggestions.map((s, i) => (
                  <span
                    key={i}
                    className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full font-medium"
                  >
                    {s}
                  </span>
                ))}
              </div>
            )}
        </div>
      )}

      {data.general_description && (
        <div className="rounded-xl border border-gray-200 bg-white p-4">
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">
            Description
          </p>
          <p className="text-sm text-gray-700">{data.general_description}</p>
        </div>
      )}

      {/* Depth profile table */}
      {data.bulk_density?.depths &&
        Object.keys(data.bulk_density.depths).length > 0 && (
          <div className="rounded-xl border border-gray-200 bg-white p-4 overflow-x-auto">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
              Depth Profile
            </p>
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="pb-2 pr-4">Depth</th>
                  <th className="pb-2 pr-4">Bulk Density</th>
                  <th className="pb-2 pr-4">pH</th>
                  <th className="pb-2 pr-4">Sand %</th>
                  <th className="pb-2 pr-4">Silt %</th>
                  <th className="pb-2">Clay %</th>
                </tr>
              </thead>
              <tbody>
                {Object.keys(data.bulk_density.depths).map((depth) => (
                  <tr key={depth} className="border-b border-gray-100">
                    <td className="py-1.5 pr-4 font-medium text-gray-700">
                      {depth}
                    </td>
                    <td className="py-1.5 pr-4">
                      {data.bulk_density?.depths?.[depth] ?? "—"}
                    </td>
                    <td className="py-1.5 pr-4">
                      {data.ph_level?.depths?.[depth] ?? "—"}
                    </td>
                    <td className="py-1.5 pr-4">
                      {data.texture?.depths?.[depth]?.sand ?? "—"}
                    </td>
                    <td className="py-1.5 pr-4">
                      {data.texture?.depths?.[depth]?.silt ?? "—"}
                    </td>
                    <td className="py-1.5">
                      {data.texture?.depths?.[depth]?.clay ?? "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

      {data.warnings.length > 0 && (
        <div className="rounded-lg bg-amber-50 border border-amber-200 p-3">
          <p className="text-xs font-medium text-amber-700">Warnings:</p>
          {data.warnings.map((w, i) => (
            <p key={i} className="text-xs text-amber-600 mt-1">
              {w}
            </p>
          ))}
        </div>
      )}

      <div className="flex gap-2 flex-wrap">
        {data.sources.map((s, i) => (
          <span
            key={i}
            className="text-xs bg-gray-100 text-gray-500 px-2 py-1 rounded-full"
          >
            {s}
          </span>
        ))}
      </div>
    </div>
  );
}

interface Props {
  title: string;
  value: string | number | null | undefined;
  unit?: string;
  subtitle?: string;
  color?: string;
}

export default function SoilCard({
  title,
  value,
  unit,
  subtitle,
  color = "emerald",
}: Props) {
  const colorClasses: Record<string, string> = {
    emerald: "border-emerald-200 bg-emerald-50",
    blue: "border-blue-200 bg-blue-50",
    amber: "border-amber-200 bg-amber-50",
    purple: "border-purple-200 bg-purple-50",
    rose: "border-rose-200 bg-rose-50",
    cyan: "border-cyan-200 bg-cyan-50",
    orange: "border-orange-200 bg-orange-50",
  };

  return (
    <div
      className={`rounded-xl border p-4 ${colorClasses[color] || colorClasses.emerald}`}
    >
      <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
        {title}
      </p>
      <p className="mt-1 text-2xl font-bold text-gray-800">
        {value != null ? value : "N/A"}
        {unit && value != null && (
          <span className="text-sm font-normal text-gray-500 ml-1">
            {unit}
          </span>
        )}
      </p>
      {subtitle && (
        <p className="mt-1 text-xs text-gray-500">{subtitle}</p>
      )}
    </div>
  );
}

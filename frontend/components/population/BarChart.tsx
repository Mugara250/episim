"use client";

// Dependency-free horizontal bar chart. The frontend has no charting library
// and this module only needs a simple population-by-area comparison, so a hand
// -rolled SVG keeps the bundle lean. A real geographic choropleth needs
// district/sector boundary polygons that don't exist until Module 9 is built.

export type BarDatum = { label: string; value: number };

export function BarChart({ data, unit = "people" }: { data: BarDatum[]; unit?: string }) {
  if (data.length === 0) {
    return <p className="text-sm text-text-secondary">No aggregated data yet — run aggregation to populate this chart.</p>;
  }

  const max = Math.max(...data.map((d) => d.value), 1);
  const rowHeight = 28;

  return (
    <div className="overflow-x-auto">
      <div className="min-w-[420px] space-y-2">
        {data.map((d) => (
          <div key={d.label} className="flex items-center gap-3" style={{ height: rowHeight }}>
            <span className="w-28 shrink-0 truncate text-right text-xs text-text-secondary" title={d.label}>
              {d.label}
            </span>
            <div className="relative h-4 flex-1 rounded bg-surface-2">
              <div
                className="absolute inset-y-0 left-0 rounded bg-brand/70"
                style={{ width: `${(d.value / max) * 100}%` }}
              />
            </div>
            <span className="w-20 shrink-0 text-xs tabular-nums text-text-primary">
              {d.value.toLocaleString()}
            </span>
          </div>
        ))}
        <p className="pt-1 text-[11px] text-text-faint">Values in {unit}. Bar length is relative to the largest group.</p>
      </div>
    </div>
  );
}

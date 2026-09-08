import type { PopulationDatasetStatus, PopulationGranularity } from "@/lib/api";

const STATUS_STYLES: Record<PopulationDatasetStatus, string> = {
  draft: "bg-surface-2 text-text-secondary",
  validated: "bg-brand/15 text-brand-light",
  archived: "bg-surface-2 text-text-faint",
};

export function StatusBadge({ status }: { status: PopulationDatasetStatus }) {
  return (
    <span className={`rounded-full px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${STATUS_STYLES[status]}`}>
      {status}
    </span>
  );
}

export function GranularityBadge({ granularity }: { granularity: PopulationGranularity }) {
  return (
    <span
      className={
        "rounded-full border px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide " +
        (granularity === "microdata"
          ? "border-info/40 text-info"
          : "border-border-strong text-text-secondary")
      }
    >
      {granularity}
    </span>
  );
}

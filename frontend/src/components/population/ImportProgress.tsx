/** Running-progress readout for a population import, driven by the fields the
 * import job writes into `population_datasets.import_report` while status is
 * `processing` (see app/services/population_jobs.py). */

export type ImportReport = {
  imported?: number;
  rejected?: number;
  rejection_samples?: string[];
  error?: string;
  phase?: string;
  rows_processed?: number;
  total_rows?: number | null;
};

export function ImportProgress({ report }: { report: ImportReport | null | undefined }) {
  const processed = report?.rows_processed ?? 0;
  const total = report?.total_rows ?? null;
  const pct = total && total > 0 ? Math.min(100, Math.round((processed / total) * 100)) : null;

  return (
    <div className="rounded-xl border border-border bg-surface p-4">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium text-text-primary">Parsing and validating rows…</span>
        <span className="text-text-secondary">
          {processed.toLocaleString()}
          {total ? ` / ${total.toLocaleString()}` : ""} rows{pct !== null ? ` · ${pct}%` : ""}
        </span>
      </div>
      <div className="mt-2 h-2 overflow-hidden rounded-full bg-surface-2">
        <div
          className={`h-full rounded-full bg-brand transition-[width] duration-500 ${pct === null ? "animate-pulse" : ""}`}
          style={{ width: pct === null ? "40%" : `${pct}%` }}
        />
      </div>
      {(report?.rejected ?? 0) > 0 && (
        <p className="mt-2 text-xs text-text-faint">{report?.rejected?.toLocaleString()} rows rejected so far</p>
      )}
    </div>
  );
}

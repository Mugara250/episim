"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { PageMeta } from "@/components/layout/app-shell-context";
import { BarChart } from "@/components/population/BarChart";
import { GranularityBadge, StatusBadge } from "@/components/population/badges";
import {
  aggregatePopulationDataset,
  getPopulationDataset,
  getPopulationDatasetVersions,
  type PopulationDataset,
  type PopulationDatasetSummary,
} from "@/lib/api";

export default function PopulationDatasetDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [dataset, setDataset] = useState<PopulationDatasetSummary | null>(null);
  const [versions, setVersions] = useState<PopulationDataset[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [aggregating, setAggregating] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const [detail, vers] = await Promise.all([
        getPopulationDataset(id),
        getPopulationDatasetVersions(id),
      ]);
      setDataset(detail);
      setVersions(vers);
      setError(null);
    } catch {
      setError("Could not load this dataset.");
    }
  }, [id]);

  useEffect(() => {
    void load();
  }, [load]);

  async function runAggregate() {
    setAggregating(true);
    setNotice(null);
    try {
      const res = await aggregatePopulationDataset(id);
      setNotice(res.detail);
      // Give the worker a moment, then refresh a couple of times.
      setTimeout(load, 2500);
      setTimeout(load, 6000);
    } catch (err) {
      setNotice(err instanceof Error ? err.message : "Could not queue aggregation.");
    } finally {
      setAggregating(false);
    }
  }

  const report = dataset?.import_report as
    | { imported?: number; rejected?: number; rejection_samples?: string[]; error?: string }
    | null
    | undefined;

  return (
    <>
      <PageMeta title={dataset?.name ?? "Dataset"} subtitle="Configuration Data · Population Data" />

      <Link href="/data/population" className="text-sm text-text-secondary hover:text-brand-light">
        ← Population Datasets
      </Link>

      {error && <p className="mt-4 text-sm text-error">{error}</p>}

      {dataset && (
        <>
          <div className="mt-2 flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-bold text-text-primary">{dataset.name}</h1>
            <StatusBadge status={dataset.status} />
            <GranularityBadge granularity={dataset.granularity} />
          </div>

          <div className="mt-6 grid gap-4 sm:grid-cols-3">
            <Stat label="Total population" value={dataset.total_population.toLocaleString()} />
            <Stat label={`Rows (${dataset.stats_source})`} value={dataset.row_count.toLocaleString()} />
            <Stat label="Version" value={String(dataset.version)} />
          </div>

          <dl className="mt-6 grid gap-x-8 gap-y-2 text-sm sm:grid-cols-2">
            <Row k="Region ID" v={dataset.region_id} />
            <Row k="Year" v={String(dataset.year)} />
            <Row k="Source" v={dataset.source} />
            <Row k="Imported / rejected" v={report ? `${report.imported ?? 0} / ${report.rejected ?? 0}` : "—"} />
          </dl>

          {report?.rejection_samples && report.rejection_samples.length > 0 && (
            <details className="mt-4 rounded-lg border border-border bg-surface p-4 text-sm">
              <summary className="cursor-pointer text-text-secondary">
                {report.rejected} rejected rows — sample reasons
              </summary>
              <ul className="mt-2 space-y-1 text-xs text-text-faint">
                {report.rejection_samples.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
            </details>
          )}

          {dataset.granularity === "microdata" && (
            <div className="mt-6">
              <button
                type="button"
                onClick={runAggregate}
                disabled={aggregating || dataset.status !== "validated"}
                className="rounded-full border border-border-strong px-4 py-2 text-sm font-semibold text-text-primary transition hover:border-brand/50 disabled:opacity-50"
              >
                {aggregating ? "Queuing…" : "Recompute aggregate (population_records)"}
              </button>
              {notice && <p className="mt-2 text-xs text-text-secondary">{notice}</p>}
            </div>
          )}

          <section className="mt-10">
            <h2 className="text-lg font-bold text-text-primary">Population by district</h2>
            <p className="mt-1 text-xs text-text-faint">
              Simplified map preview: a district-level bar chart from population_records. A true choropleth
              needs district/sector boundary polygons from Module 9 (geographic data), not yet built.
            </p>
            <div className="mt-4 rounded-2xl border border-border bg-surface p-5">
              <BarChart data={dataset.distribution.map((d) => ({ label: `District ${d.region}`, value: d.population }))} />
            </div>
          </section>

          <section className="mt-10">
            <h2 className="text-lg font-bold text-text-primary">Version history</h2>
            <p className="mt-1 text-xs text-text-faint">All imports for region <span className="text-text-secondary">{dataset.region_id}</span>.</p>
            <div className="mt-4 overflow-x-auto rounded-2xl border border-border">
              <table className="w-full min-w-[560px] text-left text-sm">
                <thead className="bg-surface text-xs uppercase tracking-wide text-text-secondary">
                  <tr>
                    <th className="px-4 py-3 font-semibold">Version</th>
                    <th className="px-4 py-3 font-semibold">Import date</th>
                    <th className="px-4 py-3 font-semibold">Rows imported / rejected</th>
                    <th className="px-4 py-3 font-semibold">Status</th>
                    <th className="px-4 py-3 font-semibold" />
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {versions.map((v) => {
                    const vr = v.import_report as { imported?: number; rejected?: number } | null;
                    return (
                      <tr key={v.id} className={v.id === dataset.id ? "bg-brand/5" : ""}>
                        <td className="px-4 py-3 text-text-primary">v{v.version}</td>
                        <td className="px-4 py-3 text-text-secondary">{new Date(v.created_at).toLocaleDateString()}</td>
                        <td className="px-4 py-3 text-text-secondary">
                          {vr ? `${vr.imported ?? 0} / ${vr.rejected ?? 0}` : "—"}
                        </td>
                        <td className="px-4 py-3"><StatusBadge status={v.status} /></td>
                        <td className="px-4 py-3 text-right">
                          {v.id !== dataset.id && (
                            <Link href={`/data/population/${v.id}`} className="text-xs text-brand-light hover:underline">
                              View
                            </Link>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-border bg-surface p-4">
      <p className="text-xs uppercase tracking-wide text-text-secondary">{label}</p>
      <p className="mt-1 text-xl font-bold text-text-primary">{value}</p>
    </div>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex justify-between border-b border-border/60 py-1">
      <dt className="text-text-secondary">{k}</dt>
      <dd className="text-text-primary">{v}</dd>
    </div>
  );
}

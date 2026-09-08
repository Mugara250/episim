"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { PageMeta } from "@/components/layout/app-shell-context";
import { GranularityBadge, StatusBadge } from "@/components/population/badges";
import {
  getPopulationDatasets,
  type PopulationDataset,
  type PopulationDatasetStatus,
} from "@/lib/api";

const STATUSES: (PopulationDatasetStatus | "")[] = ["", "draft", "validated", "archived"];

export default function PopulationBrowserPage() {
  const [datasets, setDatasets] = useState<PopulationDataset[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [region, setRegion] = useState("");
  const [year, setYear] = useState("");
  const [source, setSource] = useState("");
  const [status, setStatus] = useState<PopulationDatasetStatus | "">("");

  useEffect(() => {
    setLoading(true);
    getPopulationDatasets({
      region_id: region || undefined,
      year: year ? Number(year) : undefined,
      source: source || undefined,
      status: status || undefined,
    })
      .then((res) => {
        setDatasets(res.items);
        setTotal(res.total);
        setError(null);
      })
      .catch(() => setError("Could not load population datasets."))
      .finally(() => setLoading(false));
  }, [region, year, source, status]);

  const filtersActive = useMemo(() => region || year || source || status, [region, year, source, status]);

  return (
    <>
      <PageMeta title="Population Data" subtitle="Configuration Data · Demographic & geographic datasets" />

      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-text-primary">Population Datasets</h1>
        <Link
          href="/data/population/import"
          className="rounded-full bg-brand px-4 py-2 text-sm font-semibold text-bg transition hover:bg-brand-light"
        >
          + Import Dataset
        </Link>
      </div>

      <div className="mt-6 grid gap-3 sm:grid-cols-4">
        <input value={region} onChange={(e) => setRegion(e.target.value)} placeholder="Region ID" className="input" />
        <input value={year} onChange={(e) => setYear(e.target.value)} placeholder="Year" type="number" className="input" />
        <input value={source} onChange={(e) => setSource(e.target.value)} placeholder="Source" className="input" />
        <select value={status} onChange={(e) => setStatus(e.target.value as PopulationDatasetStatus | "")} className="input">
          {STATUSES.map((s) => (
            <option key={s} value={s}>{s ? s[0].toUpperCase() + s.slice(1) : "All statuses"}</option>
          ))}
        </select>
      </div>

      {loading && <p className="mt-6 text-sm text-text-secondary">Loading…</p>}
      {error && <p className="mt-6 text-sm text-error">{error}</p>}

      {!loading && !error && (
        <div className="mt-6 overflow-x-auto rounded-2xl border border-border">
          <table className="w-full min-w-[720px] text-left text-sm">
            <thead className="bg-surface text-xs uppercase tracking-wide text-text-secondary">
              <tr>
                <th className="px-4 py-3 font-semibold">Dataset</th>
                <th className="px-4 py-3 font-semibold">Region</th>
                <th className="px-4 py-3 font-semibold">Year</th>
                <th className="px-4 py-3 font-semibold">Source</th>
                <th className="px-4 py-3 font-semibold">Granularity</th>
                <th className="px-4 py-3 font-semibold">Status</th>
                <th className="px-4 py-3 font-semibold">Ver.</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {datasets.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-text-secondary">
                    {filtersActive ? "No datasets match these filters." : "No datasets imported yet."}
                  </td>
                </tr>
              )}
              {datasets.map((d) => (
                <tr key={d.id} className="transition hover:bg-surface/60">
                  <td className="px-4 py-3">
                    <Link href={`/data/population/${d.id}`} className="font-semibold text-text-primary hover:text-brand-light">
                      {d.name}
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-text-secondary">{d.region_id}</td>
                  <td className="px-4 py-3 text-text-secondary">{d.year}</td>
                  <td className="px-4 py-3 text-text-secondary">{d.source}</td>
                  <td className="px-4 py-3"><GranularityBadge granularity={d.granularity} /></td>
                  <td className="px-4 py-3"><StatusBadge status={d.status} /></td>
                  <td className="px-4 py-3 text-text-secondary">{d.version}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!loading && total > datasets.length && (
        <p className="mt-3 text-xs text-text-faint">Showing {datasets.length} of {total}. Refine filters to narrow results.</p>
      )}
    </>
  );
}

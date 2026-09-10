"use client";

import { useCallback, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Field } from "@/components/Field";
import { ImportProgress, type ImportReport } from "@/components/population/ImportProgress";
import {
  getPopulationDataset,
  importPopulationDataset,
  type PopulationDataset,
  type PopulationGranularity,
} from "@/lib/api";

type Step = "details" | "confirm" | "processing";

type Meta = { name: string; region_id: string; year: number; source: string };

/** Mirrors the backend's header-based detection (app/services/population_import.py)
 * so the wizard can show the user what tier the file will land in before upload. */
function detectGranularity(header: string): PopulationGranularity | null {
  const cols = new Set(header.split(",").map((c) => c.trim().toLowerCase()));
  if (cols.has("age_band") && cols.has("population_count")) return "aggregate";
  if (cols.has("household_id") || cols.has("person_id") || (cols.has("age") && cols.has("sex"))) return "microdata";
  return null;
}

export function ImportWizard() {
  const router = useRouter();
  const fileRef = useRef<HTMLInputElement>(null);
  const [step, setStep] = useState<Step>("details");
  const [meta, setMeta] = useState<Meta>({ name: "", region_id: "", year: new Date().getFullYear(), source: "NISR Census" });
  const [file, setFile] = useState<File | null>(null);
  const [detected, setDetected] = useState<PopulationGranularity | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dataset, setDataset] = useState<PopulationDataset | null>(null);

  const readHeader = useCallback(async (f: File) => {
    const slice = await f.slice(0, 8192).text();
    setDetected(detectGranularity(slice.split(/\r?\n/)[0] ?? ""));
  }, []);

  function onFile(f: File | null) {
    setFile(f);
    setDetected(null);
    if (f) void readHeader(f);
  }

  async function goConfirm(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!file) {
      setError("Choose a CSV file to import.");
      return;
    }
    if (!detected) {
      setError("Could not recognise this file's columns as microdata or aggregate. Check the header row.");
      return;
    }
    setStep("confirm");
  }

  async function submit() {
    if (!file || !detected) return;
    setError(null);
    setStep("processing");
    try {
      const created = await importPopulationDataset({ ...meta, granularity: detected, file });
      setDataset(created);
      poll(created.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Import failed to start");
      setStep("confirm");
    }
  }

  function poll(id: string) {
    const tick = async () => {
      try {
        const detail = await getPopulationDataset(id);
        setDataset(detail);
        // Keep polling while the job is queued (draft, no report yet) or running.
        if (detail.status === "processing" || (detail.status === "draft" && !detail.import_report)) {
          setTimeout(tick, 2000);
        }
      } catch {
        setTimeout(tick, 3000);
      }
    };
    setTimeout(tick, 1500);
  }

  if (step === "processing") {
    const report = dataset?.import_report as ImportReport | null | undefined;
    const done = dataset && (dataset.status === "validated" || dataset.status === "failed");

    return (
      <div className="mt-6 max-w-xl rounded-2xl border border-border bg-surface p-6">
        {!done && dataset?.status === "processing" && <ImportProgress report={report} />}
        {!done && dataset?.status !== "processing" && (
          <p className="text-sm text-text-secondary">
            Queued… the import worker will pick this up shortly. This page updates automatically.
          </p>
        )}
        {done && dataset?.status === "validated" && (
          <>
            <p className="text-sm font-semibold text-brand-light">Import complete — dataset validated.</p>
            <ul className="mt-3 space-y-1 text-sm text-text-secondary">
              <li>Rows imported: <span className="text-text-primary">{report?.imported ?? 0}</span></li>
              <li>Rows rejected: <span className="text-text-primary">{report?.rejected ?? 0}</span></li>
            </ul>
          </>
        )}
        {done && dataset?.status !== "validated" && (
          <>
            <p className="text-sm font-semibold text-error">Import did not complete.</p>
            <p className="mt-2 text-sm text-text-secondary">{report?.error ?? "The import job did not complete."}</p>
          </>
        )}
        {report?.rejection_samples && report.rejection_samples.length > 0 && (
          <div className="mt-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-text-secondary">Sample rejections</p>
            <ul className="mt-2 space-y-1 text-xs text-text-faint">
              {report.rejection_samples.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          </div>
        )}
        {done && (
          <div className="mt-6 flex gap-3">
            <button
              type="button"
              onClick={() => dataset && router.push(`/data/population/${dataset.id}`)}
              className="rounded-full bg-brand px-4 py-2 text-sm font-semibold text-bg transition hover:bg-brand-light"
            >
              View dataset
            </button>
            <button
              type="button"
              onClick={() => router.push("/data/population")}
              className="rounded-full border border-border-strong px-4 py-2 text-sm font-semibold text-text-primary transition hover:border-brand/50"
            >
              Back to browser
            </button>
          </div>
        )}
      </div>
    );
  }

  if (step === "confirm") {
    return (
      <div className="mt-6 max-w-xl rounded-2xl border border-border bg-surface p-6">
        <h2 className="text-lg font-bold text-text-primary">Confirm detected format</h2>
        <p className="mt-3 text-sm text-text-secondary">
          From the column headers, this file looks like{" "}
          <span className="font-semibold text-brand-light">{detected}</span> data.
        </p>
        <p className="mt-2 text-sm text-text-secondary">
          {detected === "microdata"
            ? "It will populate the row-per-person tier. You can aggregate it afterwards for SEIR-level models."
            : "It will populate the aggregate tier directly, skipping the microdata tier."}
        </p>
        <dl className="mt-4 space-y-1 text-sm text-text-secondary">
          <div className="flex justify-between"><dt>Name</dt><dd className="text-text-primary">{meta.name}</dd></div>
          <div className="flex justify-between"><dt>Region</dt><dd className="text-text-primary">{meta.region_id}</dd></div>
          <div className="flex justify-between"><dt>Year</dt><dd className="text-text-primary">{meta.year}</dd></div>
          <div className="flex justify-between"><dt>File</dt><dd className="text-text-primary">{file?.name}</dd></div>
        </dl>
        {error && <p className="mt-3 text-sm text-error">{error}</p>}
        <div className="mt-6 flex gap-3">
          <button type="button" onClick={() => setStep("details")} className="rounded-full border border-border-strong px-4 py-2 text-sm font-semibold text-text-primary transition hover:border-brand/50">
            Back
          </button>
          <button type="button" onClick={submit} className="rounded-full bg-brand px-4 py-2 text-sm font-semibold text-bg transition hover:bg-brand-light">
            Start import
          </button>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={goConfirm} className="mt-6 max-w-xl space-y-4">
      <Field label="Dataset name">
        <input required value={meta.name} onChange={(e) => setMeta({ ...meta, name: e.target.value })} className="input" placeholder="RPHC5 2022 (10% sample)" />
      </Field>
      <div className="grid grid-cols-2 gap-4">
        <Field label="Region ID (NISR code)">
          <input required value={meta.region_id} onChange={(e) => setMeta({ ...meta, region_id: e.target.value })} className="input" placeholder="e.g. 1 or 12 or 1101" />
        </Field>
        <Field label="Year">
          <input type="number" required value={meta.year} onChange={(e) => setMeta({ ...meta, year: Number(e.target.value) })} className="input" />
        </Field>
      </div>
      <Field label="Source">
        <input required value={meta.source} onChange={(e) => setMeta({ ...meta, source: e.target.value })} className="input" />
      </Field>
      <Field label="Census file (CSV)">
        <input
          ref={fileRef}
          type="file"
          accept=".csv,text/csv"
          onChange={(e) => onFile(e.target.files?.[0] ?? null)}
          className="block w-full text-sm text-text-secondary file:mr-3 file:rounded-full file:border-0 file:bg-brand/15 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-brand-light"
        />
      </Field>
      {file && (
        <p className="text-xs text-text-secondary">
          Detected format:{" "}
          {detected ? <span className="font-semibold text-brand-light">{detected}</span> : <span className="text-error">unrecognised headers</span>}
        </p>
      )}
      {error && <p className="text-sm text-error">{error}</p>}
      <button type="submit" className="rounded-full bg-brand px-5 py-2.5 text-sm font-semibold text-white transition hover:text-bg hover:bg-brand-dark">
        Next: confirm format
      </button>
    </form>
  );
}

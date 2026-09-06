"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { DashboardShell } from "@/components/DashboardShell";
import { getDiseasePresets, type DiseasePreset } from "@/lib/api";
import { getToken } from "@/lib/auth";

export default function DiseasePresetsPage() {
  const router = useRouter();
  const [presets, setPresets] = useState<DiseasePreset[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }
    getDiseasePresets()
      .then(setPresets)
      .catch(() => setError("Could not load disease presets."))
      .finally(() => setLoading(false));
  }, [router]);

  return (
    <DashboardShell>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-text-primary">Disease Presets</h1>
        <Link
          href="/disease-presets/new"
          className="rounded-full bg-brand px-4 py-2 text-sm font-semibold text-bg transition hover:bg-brand-light"
        >
          New preset
        </Link>
      </div>

      {loading && <p className="mt-6 text-sm text-text-secondary">Loading...</p>}
      {error && <p className="mt-6 text-sm text-error">{error}</p>}

      <div className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {presets.map((preset) => (
          <Link
            key={preset.id}
            href={`/disease-presets/${preset.id}/edit`}
            className="rounded-2xl border border-border bg-surface p-5 transition hover:border-brand/50"
          >
            <div className="flex items-start justify-between">
              <h3 className="font-bold text-text-primary">{preset.name}</h3>
              {preset.is_builtin && (
                <span className="rounded-full bg-surface-2 px-2 py-0.5 text-[10px] font-semibold uppercase text-text-secondary">
                  Built-in
                </span>
              )}
            </div>
            <dl className="mt-3 space-y-1 text-xs text-text-secondary">
              <div className="flex justify-between">
                <dt>R0</dt>
                <dd className="text-text-primary">{preset.r0}</dd>
              </div>
              <div className="flex justify-between">
                <dt>Incubation</dt>
                <dd className="text-text-primary">{preset.incubation_period_days}d</dd>
              </div>
              <div className="flex justify-between">
                <dt>Mortality</dt>
                <dd className="text-text-primary">{(preset.mortality_rate * 100).toFixed(2)}%</dd>
              </div>
              <div className="flex justify-between">
                <dt>Transmission</dt>
                <dd className="text-text-primary capitalize">{preset.transmission_route}</dd>
              </div>
            </dl>
          </Link>
        ))}
      </div>
    </DashboardShell>
  );
}

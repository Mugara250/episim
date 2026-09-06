"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Field } from "@/components/Field";
import type { DiseasePreset, DiseasePresetInput } from "@/lib/api";

const ROUTES = ["airborne", "waterborne", "contact", "vector"];

export function DiseasePresetForm({
  initial,
  disabled,
  onSubmit,
}: {
  initial?: DiseasePreset;
  disabled?: boolean;
  onSubmit: (payload: DiseasePresetInput) => Promise<void>;
}) {
  const router = useRouter();
  const [form, setForm] = useState<DiseasePresetInput>({
    name: initial?.name ?? "",
    r0: initial?.r0 ?? 1,
    incubation_period_days: initial?.incubation_period_days ?? 1,
    infectious_period_days: initial?.infectious_period_days ?? 1,
    mortality_rate: initial?.mortality_rate ?? 0,
    asymptomatic_fraction: initial?.asymptomatic_fraction ?? 0,
    transmission_route: initial?.transmission_route ?? "contact",
    source_citation: initial?.source_citation ?? "",
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function update<K extends keyof DiseasePresetInput>(key: K, value: DiseasePresetInput[K]) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await onSubmit(form);
      router.push("/disease-presets");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save preset");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mt-6 max-w-xl space-y-4">
      {disabled && (
        <p className="rounded-lg border border-border bg-surface-2 px-3 py-2 text-sm text-text-secondary">
          Built-in presets cannot be edited.
        </p>
      )}

      <Field label="Name">
        <input
          required
          disabled={disabled}
          value={form.name}
          onChange={(e) => update("name", e.target.value)}
          className="input"
        />
      </Field>

      <div className="grid grid-cols-2 gap-4">
        <Field label="R0">
          <input
            type="number"
            step="0.01"
            min="0"
            required
            disabled={disabled}
            value={form.r0}
            onChange={(e) => update("r0", Number(e.target.value))}
            className="input"
          />
        </Field>
        <Field label="Transmission route">
          <select
            disabled={disabled}
            value={form.transmission_route}
            onChange={(e) => update("transmission_route", e.target.value as DiseasePresetInput["transmission_route"])}
            className="input"
          >
            {ROUTES.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </Field>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Field label="Incubation period (days)">
          <input
            type="number"
            step="0.1"
            min="0"
            required
            disabled={disabled}
            value={form.incubation_period_days}
            onChange={(e) => update("incubation_period_days", Number(e.target.value))}
            className="input"
          />
        </Field>
        <Field label="Infectious period (days)">
          <input
            type="number"
            step="0.1"
            min="0"
            required
            disabled={disabled}
            value={form.infectious_period_days}
            onChange={(e) => update("infectious_period_days", Number(e.target.value))}
            className="input"
          />
        </Field>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Field label="Mortality rate (0-1)">
          <input
            type="number"
            step="0.001"
            min="0"
            max="1"
            required
            disabled={disabled}
            value={form.mortality_rate}
            onChange={(e) => update("mortality_rate", Number(e.target.value))}
            className="input"
          />
        </Field>
        <Field label="Asymptomatic fraction (0-1)">
          <input
            type="number"
            step="0.01"
            min="0"
            max="1"
            required
            disabled={disabled}
            value={form.asymptomatic_fraction}
            onChange={(e) => update("asymptomatic_fraction", Number(e.target.value))}
            className="input"
          />
        </Field>
      </div>

      <Field label="Source citation (optional)">
        <input
          disabled={disabled}
          value={form.source_citation ?? ""}
          onChange={(e) => update("source_citation", e.target.value)}
          className="input"
        />
      </Field>

      {error && <p className="text-sm text-error">{error}</p>}

      {!disabled && (
        <button
          type="submit"
          disabled={loading}
          className="rounded-full bg-brand px-5 py-2.5 text-sm font-semibold text-bg transition hover:bg-brand-light disabled:opacity-50"
        >
          {loading ? "Saving..." : "Save preset"}
        </button>
      )}
    </form>
  );
}

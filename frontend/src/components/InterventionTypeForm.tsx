import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Field } from "@/components/Field";
import type { InterventionType, InterventionTypeInput } from "@/lib/api";

const MECHANISMS = ["compartment_shift", "rate_multiplier"];

export function InterventionTypeForm({
  initial,
  disabled,
  onSubmit,
}: {
  initial?: InterventionType;
  disabled?: boolean;
  onSubmit: (payload: InterventionTypeInput) => Promise<void>;
}) {
  const navigate = useNavigate();
  const [form, setForm] = useState<InterventionTypeInput>({
    key: initial?.key ?? "",
    name: initial?.name ?? "",
    effect_mechanism: initial?.effect_mechanism ?? "rate_multiplier",
    default_effect_size: initial?.default_effect_size ?? 0.5,
    source_citation: initial?.source_citation ?? "",
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function update<K extends keyof InterventionTypeInput>(key: K, value: InterventionTypeInput[K]) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await onSubmit(form);
      navigate("/data/interventions/types");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save intervention type");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mt-6 max-w-xl space-y-4">
      <Field label="Key">
        <input
          required
          disabled={disabled || Boolean(initial)}
          value={form.key}
          onChange={(e) => update("key", e.target.value)}
          className="input"
        />
      </Field>

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
        <Field label="Effect mechanism">
          <select
            disabled={disabled}
            value={form.effect_mechanism}
            onChange={(e) => update("effect_mechanism", e.target.value as InterventionTypeInput["effect_mechanism"])}
            className="input"
          >
            {MECHANISMS.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Default effect size (0-1)">
          <input
            type="number"
            step="0.01"
            min="0"
            max="1"
            required
            disabled={disabled}
            value={form.default_effect_size}
            onChange={(e) => update("default_effect_size", Number(e.target.value))}
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
          {loading ? "Saving..." : "Save intervention type"}
        </button>
      )}
    </form>
  );
}

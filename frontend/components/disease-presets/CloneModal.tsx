"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { cloneDiseasePreset, type DiseasePreset } from "@/lib/api";

export function CloneModal({ preset, onClose }: { preset: DiseasePreset; onClose: () => void }) {
  const router = useRouter();
  const [name, setName] = useState(`${preset.name} (Custom)`);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleClone() {
    setError(null);
    setLoading(true);
    try {
      const clone = await cloneDiseasePreset(preset.id, name);
      router.push(`/disease-presets/${clone.id}/edit`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not clone preset");
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-6">
      <div className="w-full max-w-md rounded-2xl border border-border bg-surface p-6">
        <h2 className="text-lg font-bold text-text-primary">Clone Disease Preset</h2>
        <p className="mt-3 text-sm text-text-secondary">
          You are cloning: <span className="text-text-primary">{preset.name}</span>
        </p>

        <label className="mt-4 block">
          <span className="text-xs font-semibold uppercase tracking-wide text-text-secondary">Custom Name</span>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="input mt-1.5"
            autoFocus
          />
        </label>

        <p className="mt-3 text-xs text-text-secondary">
          This will create an editable copy with all the same parameters. You can modify the cloned preset after
          creation.
        </p>

        {error && <p className="mt-3 text-sm text-error">{error}</p>}

        <div className="mt-6 flex justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            disabled={loading}
            className="rounded-full border border-border-strong px-4 py-2 text-sm font-semibold text-text-primary transition hover:border-brand/50 disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleClone}
            disabled={loading || !name.trim()}
            className="rounded-full bg-brand px-4 py-2 text-sm font-semibold text-bg transition hover:bg-brand-light disabled:opacity-50"
          >
            {loading ? "Cloning..." : "Clone & Edit"}
          </button>
        </div>
      </div>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { DashboardShell } from "@/components/DashboardShell";
import { DiseasePresetForm } from "@/components/DiseasePresetForm";
import { PresetBadge } from "@/components/disease-presets/PresetBadge";
import { CloneModal } from "@/components/disease-presets/CloneModal";
import { deleteDiseasePreset, getDiseasePreset, updateDiseasePreset, type DiseasePreset } from "@/lib/api";

function LockBanner({ preset }: { preset: DiseasePreset }) {
  if (preset.is_builtin) {
    return (
      <div className="rounded-lg border border-border bg-surface-2 px-4 py-3 text-sm text-text-secondary">
        🔒 <span className="font-semibold text-text-primary">Built-in Preset — Read Only.</span> This preset is
        shared across the system. To create a custom version, use &ldquo;Clone as Custom&rdquo; below.
      </div>
    );
  }
  return (
    <div className="rounded-lg border border-border bg-surface-2 px-4 py-3 text-sm text-text-secondary">
      🔒 <span className="font-semibold text-text-primary">Read Only.</span> You can only edit presets you created —
      clone this one to create your own editable copy.
    </div>
  );
}

function EditableBanner({ preset }: { preset: DiseasePreset }) {
  const label = preset.is_builtin
    ? "🔓 Built-in Preset — Editable (admin privileges). Changes affect every scenario using this shared preset."
    : "✅ Custom Preset — Editable.";
  return (
    <div className="rounded-lg border border-brand/30 bg-brand/10 px-4 py-3 text-sm text-text-secondary">
      <span className="font-semibold text-text-primary">{label}</span>
    </div>
  );
}

export default function EditDiseasePresetPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [preset, setPreset] = useState<DiseasePreset | null>(null);
  const [clonedFrom, setClonedFrom] = useState<DiseasePreset | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cloning, setCloning] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    getDiseasePreset(params.id)
      .then(async (p) => {
        setPreset(p);
        if (p.cloned_from_id) {
          try {
            setClonedFrom(await getDiseasePreset(p.cloned_from_id));
          } catch {
            // source preset may have been deleted since; not fatal
          }
        }
      })
      .catch(() => setError("Could not load this preset."));
  }, [params.id]);

  async function handleDelete() {
    if (!preset) return;
    if (!window.confirm(`Delete "${preset.name}"? This cannot be undone.`)) return;
    setDeleting(true);
    try {
      await deleteDiseasePreset(preset.id);
      router.push("/disease-presets");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not delete preset");
      setDeleting(false);
    }
  }

  return (
    <DashboardShell>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-text-primary">{preset ? preset.name : "Disease Preset"}</h1>
        {preset && <PresetBadge isBuiltin={preset.is_builtin} />}
      </div>

      {error && <p className="mt-4 text-sm text-error">{error}</p>}

      {preset && (
        <div className="max-w-xl">
          <div className="mt-4">
            {preset.permissions.can_edit ? <EditableBanner preset={preset} /> : <LockBanner preset={preset} />}
          </div>

          {clonedFrom && (
            <p className="mt-3 text-sm text-text-secondary">
              Cloned from:{" "}
              <Link href={`/disease-presets/${clonedFrom.id}/edit`} className="text-brand-light hover:underline">
                {clonedFrom.name}
              </Link>
            </p>
          )}

          <DiseasePresetForm
            initial={preset}
            disabled={!preset.permissions.can_edit}
            onSubmit={(payload) => updateDiseasePreset(preset.id, payload).then(() => undefined)}
          />

          <div className="mt-6 flex flex-wrap gap-3">
            {preset.permissions.can_clone && (
              <button
                type="button"
                onClick={() => setCloning(true)}
                className="rounded-full border border-border-strong px-4 py-2 text-sm font-semibold text-text-primary transition hover:border-brand/50"
              >
                Clone as Custom
              </button>
            )}
            {preset.permissions.can_delete && (
              <button
                type="button"
                onClick={handleDelete}
                disabled={deleting}
                className="rounded-full border border-error/40 px-4 py-2 text-sm font-semibold text-error transition hover:bg-error/10 disabled:opacity-50"
              >
                {deleting ? "Deleting..." : "Delete"}
              </button>
            )}
            <Link
              href="/disease-presets"
              className="rounded-full border border-border-strong px-4 py-2 text-sm font-semibold text-text-primary transition hover:border-brand/50"
            >
              Back to Library
            </Link>
          </div>
        </div>
      )}

      {preset && cloning && <CloneModal preset={preset} onClose={() => setCloning(false)} />}
    </DashboardShell>
  );
}

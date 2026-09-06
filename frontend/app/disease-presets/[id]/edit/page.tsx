"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { DashboardShell } from "@/components/DashboardShell";
import { DiseasePresetForm } from "@/components/DiseasePresetForm";
import { getDiseasePreset, updateDiseasePreset, type DiseasePreset } from "@/lib/api";

export default function EditDiseasePresetPage() {
  const params = useParams<{ id: string }>();
  const [preset, setPreset] = useState<DiseasePreset | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getDiseasePreset(params.id)
      .then(setPreset)
      .catch(() => setError("Could not load this preset."));
  }, [params.id]);

  return (
    <DashboardShell>
      <h1 className="text-2xl font-bold text-text-primary">Edit Disease Preset</h1>
      {error && <p className="mt-4 text-sm text-error">{error}</p>}
      {preset && (
        <DiseasePresetForm
          initial={preset}
          disabled={preset.is_builtin}
          onSubmit={(payload) => updateDiseasePreset(preset.id, payload).then(() => undefined)}
        />
      )}
    </DashboardShell>
  );
}

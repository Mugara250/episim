"use client";

import { DashboardShell } from "@/components/DashboardShell";
import { DiseasePresetForm } from "@/components/DiseasePresetForm";
import { createDiseasePreset } from "@/lib/api";

export default function NewDiseasePresetPage() {
  return (
    <DashboardShell>
      <h1 className="text-2xl font-bold text-text-primary">New Disease Preset</h1>
      <DiseasePresetForm onSubmit={(payload) => createDiseasePreset(payload).then(() => undefined)} />
    </DashboardShell>
  );
}

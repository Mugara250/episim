"use client";

import Link from "next/link";
import { DiseasePresetForm } from "@/components/DiseasePresetForm";
import { PageMeta, useAppShell } from "@/components/layout/app-shell-context";
import { createDiseasePreset } from "@/lib/api";
import { canCreatePresets } from "@/lib/permissions";

export default function NewDiseasePresetPage() {
  const { user } = useAppShell();

  if (!canCreatePresets(user)) {
    return (
      <>
        <PageMeta title="New Disease Preset" />
        <h1 className="text-2xl font-bold text-text-primary">New Disease Preset</h1>
        <p className="mt-4 max-w-xl text-sm text-text-secondary">
          Only administrators and epidemiologists with admin privileges can create new disease presets from
          scratch. You can still{" "}
          <Link href="/disease-presets" className="text-brand-light hover:underline">
            clone an existing preset
          </Link>{" "}
          into your own editable copy.
        </p>
      </>
    );
  }

  return (
    <>
      <PageMeta title="New Disease Preset" />
      <h1 className="text-2xl font-bold text-text-primary">New Disease Preset</h1>
      <DiseasePresetForm onSubmit={(payload) => createDiseasePreset(payload).then(() => undefined)} />
    </>
  );
}

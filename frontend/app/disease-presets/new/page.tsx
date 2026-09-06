"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { DashboardShell } from "@/components/DashboardShell";
import { DiseasePresetForm } from "@/components/DiseasePresetForm";
import { createDiseasePreset, getMe, type User } from "@/lib/api";
import { canCreatePresets } from "@/lib/permissions";

export default function NewDiseasePresetPage() {
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getMe()
      .then(setUser)
      .catch(() => setError("Could not load your profile."));
  }, []);

  if (error) {
    return (
      <DashboardShell>
        <p className="text-sm text-error">{error}</p>
      </DashboardShell>
    );
  }

  if (user && !canCreatePresets(user)) {
    return (
      <DashboardShell>
        <h1 className="text-2xl font-bold text-text-primary">New Disease Preset</h1>
        <p className="mt-4 max-w-xl text-sm text-text-secondary">
          Only administrators and epidemiologists with admin privileges can create new disease presets from
          scratch. You can still{" "}
          <Link href="/disease-presets" className="text-brand-light hover:underline">
            clone an existing preset
          </Link>{" "}
          into your own editable copy.
        </p>
      </DashboardShell>
    );
  }

  return (
    <DashboardShell>
      <h1 className="text-2xl font-bold text-text-primary">New Disease Preset</h1>
      {user && <DiseasePresetForm onSubmit={(payload) => createDiseasePreset(payload).then(() => undefined)} />}
    </DashboardShell>
  );
}

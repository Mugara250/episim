"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { DashboardShell } from "@/components/DashboardShell";
import { PresetBadge } from "@/components/disease-presets/PresetBadge";
import { CloneModal } from "@/components/disease-presets/CloneModal";
import { getDiseasePresets, getMe, getUserPublic, type DiseasePreset, type User, type UserPublic } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { canCreatePresets } from "@/lib/permissions";
import { roleLabel } from "@/lib/roles";

export default function DiseasePresetsPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [presets, setPresets] = useState<DiseasePreset[]>([]);
  const [creators, setCreators] = useState<Record<string, UserPublic>>({});
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [cloning, setCloning] = useState<DiseasePreset | null>(null);

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }
    Promise.all([getMe(), getDiseasePresets()])
      .then(async ([me, list]) => {
        setUser(me);
        setPresets(list);

        const otherCreatorIds = Array.from(
          new Set(
            list
              .map((p) => p.created_by)
              .filter((id): id is string => Boolean(id) && id !== me.id)
          )
        );
        const lookups = await Promise.allSettled(otherCreatorIds.map((id) => getUserPublic(id)));
        const found: Record<string, UserPublic> = {};
        lookups.forEach((result, i) => {
          if (result.status === "fulfilled") found[otherCreatorIds[i]] = result.value;
        });
        setCreators(found);
      })
      .catch(() => setError("Could not load disease presets."))
      .finally(() => setLoading(false));
  }, [router]);

  function presetById(id: string) {
    return presets.find((p) => p.id === id);
  }

  function createdByLabel(preset: DiseasePreset): string {
    if (preset.is_builtin) return "System";
    if (preset.permissions.is_owner) return "You";
    const creator = preset.created_by ? creators[preset.created_by] : undefined;
    return creator ? `${creator.full_name} (${roleLabel(creator.role)})` : "Another user";
  }

  return (
    <DashboardShell>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-text-primary">Disease Preset Library</h1>
        {user && canCreatePresets(user) && (
          <Link
            href="/disease-presets/new"
            className="rounded-full bg-brand px-4 py-2 text-sm font-semibold text-bg transition hover:bg-brand-light"
          >
            + Create New Preset
          </Link>
        )}
      </div>

      {loading && <p className="mt-6 text-sm text-text-secondary">Loading...</p>}
      {error && <p className="mt-6 text-sm text-error">{error}</p>}

      <div className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {presets.map((preset) => {
          const source = preset.cloned_from_id ? presetById(preset.cloned_from_id) : null;
          return (
            <div key={preset.id} className="rounded-2xl border border-border bg-surface p-5">
              <div className="flex items-start justify-between gap-2">
                <Link href={`/disease-presets/${preset.id}/edit`} className="font-bold text-text-primary hover:underline">
                  {preset.name}
                </Link>
                <PresetBadge isBuiltin={preset.is_builtin} />
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
                  <dt>Infectious</dt>
                  <dd className="text-text-primary">{preset.infectious_period_days}d</dd>
                </div>
              </dl>

              <p className="mt-3 text-xs text-text-secondary">Created by: {createdByLabel(preset)}</p>
              {source && <p className="text-xs text-text-secondary">Cloned from: {source.name}</p>}

              {preset.permissions.can_clone && (
                <button
                  type="button"
                  onClick={() => setCloning(preset)}
                  className="mt-4 w-full rounded-full border border-border-strong px-3 py-1.5 text-xs font-semibold text-text-primary transition hover:border-brand/50"
                >
                  Clone as Custom
                </button>
              )}
            </div>
          );
        })}
      </div>

      {cloning && <CloneModal preset={cloning} onClose={() => setCloning(null)} />}
    </DashboardShell>
  );
}

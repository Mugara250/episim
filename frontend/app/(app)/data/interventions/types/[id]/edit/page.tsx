"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { InterventionTypeForm } from "@/components/InterventionTypeForm";
import { PageMeta } from "@/components/layout/app-shell-context";
import { TypeBadge } from "@/components/intervention-types/TypeBadge";
import { CloneTypeModal } from "@/components/intervention-types/CloneTypeModal";
import { getInterventionType, updateInterventionType, type InterventionType } from "@/lib/api";

function LockBanner({ type }: { type: InterventionType }) {
  if (type.is_builtin) {
    return (
      <div className="rounded-lg border border-border bg-surface-2 px-4 py-3 text-sm text-text-secondary">
        🔒 <span className="font-semibold text-text-primary">Built-in Type — Read Only.</span> This intervention
        type is shared across the system. To create a custom version, use &ldquo;Clone as Custom&rdquo; below.
      </div>
    );
  }
  return (
    <div className="rounded-lg border border-border bg-surface-2 px-4 py-3 text-sm text-text-secondary">
      🔒 <span className="font-semibold text-text-primary">Read Only.</span> You can only edit intervention types
      you created — clone this one to create your own editable copy.
    </div>
  );
}

function EditableBanner({ type }: { type: InterventionType }) {
  const label = type.is_builtin
    ? "🔓 Built-in Type — Editable (admin privileges). Changes affect every package using this shared type."
    : "✅ Custom Type — Editable.";
  return (
    <div className="rounded-lg border border-brand/30 bg-brand/10 px-4 py-3 text-sm text-text-secondary">
      <span className="font-semibold text-text-primary">{label}</span>
    </div>
  );
}

export default function EditInterventionTypePage() {
  const params = useParams<{ id: string }>();
  const [type, setType] = useState<InterventionType | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cloning, setCloning] = useState(false);

  useEffect(() => {
    getInterventionType(params.id)
      .then(setType)
      .catch(() => setError("Could not load this intervention type."));
  }, [params.id]);

  return (
    <>
      <PageMeta title={type ? type.name : "Intervention Type"} subtitle="Edit intervention type" />
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-text-primary">{type ? type.name : "Intervention Type"}</h1>
        {type && <TypeBadge isBuiltin={type.is_builtin} />}
      </div>

      {error && <p className="mt-4 text-sm text-error">{error}</p>}

      {type && (
        <div className="max-w-xl">
          <div className="mt-4">{type.permissions.can_edit ? <EditableBanner type={type} /> : <LockBanner type={type} />}</div>

          <InterventionTypeForm
            initial={type}
            disabled={!type.permissions.can_edit}
            onSubmit={(payload) => updateInterventionType(type.id, payload).then(() => undefined)}
          />

          <div className="mt-6 flex flex-wrap gap-3">
            {type.permissions.can_clone && (
              <button
                type="button"
                onClick={() => setCloning(true)}
                className="rounded-full border border-border-strong px-4 py-2 text-sm font-semibold text-text-primary transition hover:border-brand/50"
              >
                Clone as Custom
              </button>
            )}
            <Link
              href="/data/interventions/types"
              className="rounded-full border border-border-strong px-4 py-2 text-sm font-semibold text-text-primary transition hover:border-brand/50"
            >
              Back to Library
            </Link>
          </div>
        </div>
      )}

      {type && cloning && <CloneTypeModal type={type} onClose={() => setCloning(false)} />}
    </>
  );
}

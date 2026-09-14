import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { TypeBadge } from "@/components/intervention-types/TypeBadge";
import { CloneTypeModal } from "@/components/intervention-types/CloneTypeModal";
import { PageMeta } from "@/components/layout/app-shell-context";
import { getInterventionTypes, type InterventionType } from "@/lib/api";

export default function InterventionTypesPage() {
  const [types, setTypes] = useState<InterventionType[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [cloning, setCloning] = useState<InterventionType | null>(null);

  useEffect(() => {
    getInterventionTypes()
      .then(setTypes)
      .catch(() => setError("Could not load intervention types."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <>
      <PageMeta title="Intervention Types" subtitle="Configuration Data · Intervention type library" />
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Intervention Types</h1>
          <p className="mt-1 text-sm text-text-secondary">
            The reference library of intervention kinds and their default effect sizes, used when building
            intervention packages.
          </p>
        </div>
        <Link
          to="/data/interventions/types/new"
          className="rounded-full bg-brand px-4 py-2 text-sm font-semibold text-bg transition hover:bg-brand-light"
        >
          + Create Custom Type
        </Link>
      </div>

      {loading && <p className="mt-6 text-sm text-text-secondary">Loading...</p>}
      {error && <p className="mt-6 text-sm text-error">{error}</p>}

      <div className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {types.map((type) => (
          <div key={type.id} className="rounded-2xl border border-border bg-surface p-5">
            <div className="flex items-start justify-between gap-2">
              <Link
                to={`/data/interventions/types/${type.id}/edit`}
                className="font-bold text-text-primary hover:underline"
              >
                {type.name}
              </Link>
              <TypeBadge isBuiltin={type.is_builtin} />
            </div>

            <dl className="mt-3 space-y-1 text-xs text-text-secondary">
              <div className="flex justify-between">
                <dt>Mechanism</dt>
                <dd className="text-text-primary">{type.effect_mechanism}</dd>
              </div>
              <div className="flex justify-between">
                <dt>Default effect size</dt>
                <dd className="text-text-primary">{type.default_effect_size}</dd>
              </div>
            </dl>

            {type.source_citation && <p className="mt-3 text-xs text-text-secondary">{type.source_citation}</p>}

            <div className="mt-4 flex gap-2">
              {type.permissions.can_edit && (
                <Link
                  to={`/data/interventions/types/${type.id}/edit`}
                  className="flex-1 rounded-full bg-brand/15 px-3 py-1.5 text-center text-xs font-semibold text-brand-light transition hover:bg-brand/25"
                >
                  Edit
                </Link>
              )}
              {type.permissions.can_clone && (
                <button
                  type="button"
                  onClick={() => setCloning(type)}
                  className="flex-1 rounded-full border border-border-strong px-3 py-1.5 text-xs font-semibold text-text-primary transition hover:text-bg hover:bg-brand-light"
                >
                  Clone as Custom
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {cloning && <CloneTypeModal type={cloning} onClose={() => setCloning(null)} />}
    </>
  );
}

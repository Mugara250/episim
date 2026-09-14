import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { PageMeta, useAppShell } from "@/components/layout/app-shell-context";
import {
  getInterventionPackages,
  getUserPublic,
  type InterventionPackage,
  type UserPublic,
} from "@/lib/api";
import { fullName } from "@/lib/name";
import { roleLabel } from "@/lib/roles";

export default function InterventionPackagesPage() {
  const { user } = useAppShell();
  const [packages, setPackages] = useState<InterventionPackage[]>([]);
  const [creators, setCreators] = useState<Record<string, UserPublic>>({});
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getInterventionPackages()
      .then(async (res) => {
        setPackages(res.items);
        setTotal(res.total);

        const otherCreatorIds = Array.from(
          new Set(res.items.map((p) => p.created_by).filter((id) => id !== user.id)),
        );
        const lookups = await Promise.allSettled(otherCreatorIds.map((id) => getUserPublic(id)));
        const found: Record<string, UserPublic> = {};
        lookups.forEach((result, i) => {
          if (result.status === "fulfilled") found[otherCreatorIds[i]] = result.value;
        });
        setCreators(found);
      })
      .catch(() => setError("Could not load intervention packages."))
      .finally(() => setLoading(false));
  }, [user]);

  function createdByLabel(pkg: InterventionPackage): string {
    if (pkg.permissions.is_owner) return "You";
    const creator = creators[pkg.created_by];
    return creator ? `${fullName(creator)} (${roleLabel(creator.role)})` : "Another user";
  }

  return (
    <>
      <PageMeta title="Intervention Packages" subtitle="Configuration Data · Intervention scenarios" />
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Intervention Packages</h1>
          <p className="mt-1 text-sm text-text-secondary">
            Named, reusable bundles of time-boxed interventions that can be attached to simulation scenarios.
          </p>
        </div>
        <div className="flex gap-2">
          <Link
            to="/data/interventions/types"
            className="rounded-full border border-border-strong px-4 py-2 text-sm font-semibold text-text-primary transition hover:text-bg hover:bg-brand-light"
          >
            Manage Intervention Types
          </Link>
          <Link
            to="/data/interventions/new"
            className="rounded-full bg-brand px-4 py-2 text-sm font-semibold text-bg transition hover:bg-brand-light"
          >
            + New Package
          </Link>
        </div>
      </div>

      {loading && <p className="mt-6 text-sm text-text-secondary">Loading...</p>}
      {error && <p className="mt-6 text-sm text-error">{error}</p>}

      {!loading && !error && packages.length === 0 && (
        <p className="mt-6 text-sm text-text-secondary">No intervention packages yet. Create one to get started.</p>
      )}

      <div className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {packages.map((pkg) => (
          <Link
            key={pkg.id}
            to={`/data/interventions/${pkg.id}`}
            className="rounded-2xl border border-border bg-surface p-5 transition hover:border-brand/50"
          >
            <div className="font-bold text-text-primary">{pkg.name}</div>
            {pkg.description && <p className="mt-1 text-xs text-text-secondary">{pkg.description}</p>}
            <dl className="mt-3 space-y-1 text-xs text-text-secondary">
              <div className="flex justify-between">
                <dt>Items</dt>
                <dd className="text-text-primary">{pkg.item_count}</dd>
              </div>
              <div className="flex justify-between">
                <dt>Created by</dt>
                <dd className="text-text-primary">{createdByLabel(pkg)}</dd>
              </div>
            </dl>
          </Link>
        ))}
      </div>

      {!loading && total > packages.length && (
        <p className="mt-3 text-xs text-text-faint">
          Showing {packages.length} of {total}. Refine filters to narrow results.
        </p>
      )}
    </>
  );
}

import { useCallback, useEffect, useMemo, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { Field } from "@/components/Field";
import { PageMeta } from "@/components/layout/app-shell-context";
import {
  addInterventionItem,
  deleteInterventionPackage,
  getInterventionPackage,
  getInterventionTypes,
  removeInterventionItem,
  type InterventionItem,
  type InterventionPackageDetail,
  type InterventionType,
} from "@/lib/api";

export default function InterventionPackageBuilderPage() {
  const params = useParams<{ id: string }>() as { id: string };
  const navigate = useNavigate();

  const [pkg, setPkg] = useState<InterventionPackageDetail | null>(null);
  const [types, setTypes] = useState<InterventionType[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  const load = useCallback(() => {
    return getInterventionPackage(params.id)
      .then(setPkg)
      .catch(() => setError("Could not load this intervention package."));
  }, [params.id]);

  useEffect(() => {
    void load();
    getInterventionTypes().then(setTypes).catch(() => undefined);
  }, [load]);

  async function handleDeletePackage() {
    if (!pkg) return;
    if (!window.confirm(`Delete "${pkg.name}"? This will also remove its items and cannot be undone.`)) return;
    setDeleting(true);
    try {
      await deleteInterventionPackage(pkg.id);
      navigate("/data/interventions");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not delete package");
      setDeleting(false);
    }
  }

  async function handleRemoveItem(item: InterventionItem) {
    if (!pkg) return;
    try {
      await removeInterventionItem(pkg.id, item.id);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not remove item");
    }
  }

  return (
    <>
      <PageMeta title={pkg ? pkg.name : "Intervention Package"} subtitle="Package builder" />
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">{pkg ? pkg.name : "Intervention Package"}</h1>
          {pkg?.description && <p className="mt-1 text-sm text-text-secondary">{pkg.description}</p>}
        </div>
        <Link
          to="/data/interventions"
          className="rounded-full border border-border-strong px-4 py-2 text-sm font-semibold text-text-primary transition hover:text-bg hover:bg-brand-light"
        >
          Back to Library
        </Link>
      </div>

      {error && <p className="mt-4 text-sm text-error">{error}</p>}

      {pkg && (
        <div className="mt-6 grid gap-6 lg:grid-cols-2">
          <div>
            <h2 className="text-sm font-semibold uppercase tracking-wide text-text-secondary">Items</h2>
            <ItemList items={pkg.items} canEdit={pkg.permissions.can_edit} onRemove={handleRemoveItem} />
          </div>

          <div>
            <h2 className="text-sm font-semibold uppercase tracking-wide text-text-secondary">Add Item</h2>
            {pkg.permissions.can_edit ? (
              <AddItemForm packageId={pkg.id} types={types} onAdded={load} />
            ) : (
              <p className="mt-3 text-sm text-text-secondary">
                🔒 Only the creator of this package can add or remove items.
              </p>
            )}
          </div>
        </div>
      )}

      {pkg?.permissions.can_delete && (
        <div className="mt-8">
          <button
            type="button"
            onClick={handleDeletePackage}
            disabled={deleting}
            className="rounded-full border border-error/40 px-4 py-2 text-sm font-semibold text-error transition hover:bg-error/10 disabled:opacity-50"
          >
            {deleting ? "Deleting..." : "Delete Package"}
          </button>
        </div>
      )}
    </>
  );
}

function ItemList({
  items,
  canEdit,
  onRemove,
}: {
  items: InterventionItem[];
  canEdit: boolean;
  onRemove: (item: InterventionItem) => void;
}) {
  if (items.length === 0) {
    return <p className="mt-3 text-sm text-text-secondary">No items yet. Add one on the right.</p>;
  }

  return (
    <div className="mt-3 space-y-2">
      {items.map((item) => (
        <div key={item.id} className="rounded-xl border border-border bg-surface p-4">
          <div className="flex items-start justify-between gap-2">
            <div>
              <p className="font-semibold text-text-primary">{item.type_name}</p>
              <p className="text-xs text-text-secondary">{item.effect_mechanism}</p>
            </div>
            {canEdit && (
              <button
                type="button"
                onClick={() => onRemove(item)}
                className="rounded-full border border-error/40 px-3 py-1 text-xs font-semibold text-error transition hover:bg-error/10"
              >
                Remove
              </button>
            )}
          </div>
          <dl className="mt-3 space-y-1 text-xs text-text-secondary">
            <div className="flex justify-between">
              <dt>Days</dt>
              <dd className="text-text-primary">
                {item.start_day} – {item.end_day ?? "ongoing"}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt>Coverage</dt>
              <dd className="text-text-primary">{item.coverage}</dd>
            </div>
            <div className="flex justify-between">
              <dt>Effect size</dt>
              <dd className="text-text-primary">
                {item.effectiveness_override ?? "default"}
                {item.effectiveness_override != null && (
                  <span className="ml-1 text-text-faint">(override)</span>
                )}
              </dd>
            </div>
          </dl>
        </div>
      ))}
    </div>
  );
}

function AddItemForm({
  packageId,
  types,
  onAdded,
}: {
  packageId: string;
  types: InterventionType[];
  onAdded: () => Promise<void> | void;
}) {
  const [typeId, setTypeId] = useState("");
  const [startDay, setStartDay] = useState(0);
  const [ongoing, setOngoing] = useState(true);
  const [endDay, setEndDay] = useState(30);
  const [coverage, setCoverage] = useState(0.5);
  const [useOverride, setUseOverride] = useState(false);
  const [override, setOverride] = useState(0.5);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!typeId && types.length > 0) setTypeId(types[0].id);
  }, [types, typeId]);

  const selectedType = useMemo(() => types.find((t) => t.id === typeId), [types, typeId]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await addInterventionItem(packageId, {
        type_id: typeId,
        start_day: startDay,
        end_day: ongoing ? null : endDay,
        coverage,
        effectiveness_override: useOverride ? override : null,
      });
      setStartDay(0);
      setOngoing(true);
      setEndDay(30);
      setCoverage(0.5);
      setUseOverride(false);
      await onAdded();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not add item");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mt-3 space-y-4 rounded-xl border border-border bg-surface p-4">
      <Field label="Intervention type">
        <select value={typeId} onChange={(e) => setTypeId(e.target.value)} className="input">
          {types.map((t) => (
            <option key={t.id} value={t.id}>
              {t.name} ({t.effect_mechanism})
            </option>
          ))}
        </select>
      </Field>

      <div className="grid grid-cols-2 gap-4">
        <Field label="Start day">
          <input
            type="number"
            min="0"
            required
            value={startDay}
            onChange={(e) => setStartDay(Number(e.target.value))}
            className="input"
          />
        </Field>
        <Field label="End day">
          <div className="space-y-1.5">
            <input
              type="number"
              min={startDay}
              disabled={ongoing}
              value={ongoing ? "" : endDay}
              placeholder={ongoing ? "ongoing" : undefined}
              onChange={(e) => setEndDay(Number(e.target.value))}
              className="input"
            />
            <label className="flex items-center gap-2 text-xs text-text-secondary">
              <input type="checkbox" checked={ongoing} onChange={(e) => setOngoing(e.target.checked)} />
              Ongoing (no end day)
            </label>
          </div>
        </Field>
      </div>

      <Field label={`Coverage (0-1): ${coverage}`}>
        <input
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={coverage}
          onChange={(e) => setCoverage(Number(e.target.value))}
          className="w-full"
        />
      </Field>

      <div>
        <label className="flex items-center gap-2 text-xs text-text-secondary">
          <input type="checkbox" checked={useOverride} onChange={(e) => setUseOverride(e.target.checked)} />
          Override effect size for this item
        </label>
        {selectedType && (
          <p className="mt-1 text-xs text-text-faint">
            Default for {selectedType.name}: {selectedType.default_effect_size}
          </p>
        )}
        {useOverride && (
          <input
            type="number"
            min="0"
            max="1"
            step="0.01"
            value={override}
            onChange={(e) => setOverride(Number(e.target.value))}
            className="input mt-2"
          />
        )}
      </div>

      {error && <p className="text-sm text-error">{error}</p>}

      <button
        type="submit"
        disabled={loading || !typeId}
        className="rounded-full bg-brand px-5 py-2.5 text-sm font-semibold text-bg transition hover:bg-brand-light disabled:opacity-50"
      >
        {loading ? "Adding..." : "Add item"}
      </button>
    </form>
  );
}

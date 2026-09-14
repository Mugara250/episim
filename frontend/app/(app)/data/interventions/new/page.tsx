"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Field } from "@/components/Field";
import { PageMeta } from "@/components/layout/app-shell-context";
import { createInterventionPackage } from "@/lib/api";

export default function NewInterventionPackagePage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const pkg = await createInterventionPackage({ name, description: description || null });
      router.push(`/data/interventions/${pkg.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create package");
      setLoading(false);
    }
  }

  return (
    <>
      <PageMeta title="New Intervention Package" />
      <h1 className="text-2xl font-bold text-text-primary">New Intervention Package</h1>
      <p className="mt-1 max-w-xl text-sm text-text-secondary">
        Give this package a name and description. You&rsquo;ll add intervention items to it on the next screen.
      </p>

      <form onSubmit={handleSubmit} className="mt-6 max-w-xl space-y-4">
        <Field label="Name">
          <input required value={name} onChange={(e) => setName(e.target.value)} className="input" autoFocus />
        </Field>
        <Field label="Description (optional)">
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="input"
            rows={3}
          />
        </Field>

        {error && <p className="text-sm text-error">{error}</p>}

        <button
          type="submit"
          disabled={loading || !name.trim()}
          className="rounded-full bg-brand px-5 py-2.5 text-sm font-semibold text-bg transition hover:bg-brand-light disabled:opacity-50"
        >
          {loading ? "Creating..." : "Create package"}
        </button>
      </form>
    </>
  );
}

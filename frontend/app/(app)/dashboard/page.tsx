"use client";

import { PageMeta, useAppShell } from "@/components/layout/app-shell-context";
import { fullName } from "@/lib/name";
import { roleLabel } from "@/lib/roles";

export default function DashboardPage() {
  const { user } = useAppShell();

  return (
    <>
      <PageMeta
        title="Epidemic Intelligence Dashboard"
        subtitle="Rwanda National Surveillance · Epidemiology Team"
      />

      <div className="rounded-2xl border border-border bg-surface p-6">
        <p className="text-sm text-text-secondary">Welcome back,</p>
        <p className="mt-1 text-xl font-bold text-text-primary">{fullName(user)}</p>
        <span className="mt-3 inline-flex items-center gap-2 rounded-full border border-border bg-surface-2 px-3 py-1 text-xs font-medium text-brand-light">
          <span className="h-1.5 w-1.5 rounded-full bg-brand" />
          {roleLabel(user.role)}
        </span>
      </div>

      <p className="mt-8 text-sm text-text-secondary">
        Simulation dashboards and widgets will appear here as more modules are built out.
      </p>
    </>
  );
}

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { DashboardShell } from "@/components/DashboardShell";
import { getMe, type User } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { fullName } from "@/lib/name";
import { roleLabel } from "@/lib/roles";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }
    getMe()
      .then(setUser)
      .catch(() => setError("Could not load your profile. Please sign in again."));
  }, [router]);

  return (
    <DashboardShell>
      <h1 className="text-2xl font-bold text-text-primary">Dashboard</h1>

      {error && <p className="mt-4 text-sm text-error">{error}</p>}

      {user && (
        <div className="mt-6 rounded-2xl border border-border bg-surface p-6">
          <p className="text-sm text-text-secondary">Welcome back,</p>
          <p className="mt-1 text-xl font-bold text-text-primary">{fullName(user)}</p>
          <span className="mt-3 inline-flex items-center gap-2 rounded-full border border-border bg-surface-2 px-3 py-1 text-xs font-medium text-brand-light">
            <span className="h-1.5 w-1.5 rounded-full bg-brand" />
            {roleLabel(user.role)}
          </span>
        </div>
      )}

      <p className="mt-8 text-sm text-text-secondary">
        Simulation dashboards and widgets will appear here as more modules are built out.
      </p>
    </DashboardShell>
  );
}

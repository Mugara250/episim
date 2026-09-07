"use client";

import { useEffect, useState, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { getMe, type User } from "@/lib/api";
import { clearSession, getToken } from "@/lib/auth";

// Shared layout for every authenticated route. Route groups don't affect the
// URL, so pages here keep their paths (/dashboard, /disease-presets, ...) while
// all inheriting the sidebar + top bar without re-implementing them.
export default function AppLayout({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [redirecting, setRedirecting] = useState(false);

  useEffect(() => {
    if (!getToken()) {
      setRedirecting(true);
      router.replace("/login");
      return;
    }
    getMe()
      .then(setUser)
      .catch(() => {
        clearSession();
        setRedirecting(true);
        router.replace("/login");
      });
  }, [router]);

  function signOut() {
    clearSession();
    router.replace("/login");
  }

  if (!user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-bg text-sm text-text-secondary">
        {redirecting ? "Redirecting to sign in…" : "Loading…"}
      </div>
    );
  }

  return (
    <AppShell user={user} onSignOut={signOut}>
      {children}
    </AppShell>
  );
}

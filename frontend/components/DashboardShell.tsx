"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import type { ReactNode } from "react";
import { clearSession } from "@/lib/auth";

const NAV = [
  { label: "Dashboard", href: "/dashboard" },
  { label: "Disease Presets", href: "/disease-presets" },
];

export function DashboardShell({ children }: { children: ReactNode }) {
  const router = useRouter();

  function handleLogout() {
    clearSession();
    router.push("/login");
  }

  return (
    <div className="min-h-screen">
      <header className="border-b border-border bg-surface/60">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-8">
            <Link href="/dashboard" className="flex items-center gap-2">
              <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-brand text-bg">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M3 12h4l2 8 4-16 2 8h6" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </span>
              <span className="font-bold text-text-primary">EpiSim</span>
            </Link>
            <nav className="flex gap-6">
              {NAV.map((item) => (
                <Link key={item.href} href={item.href} className="text-sm text-text-secondary hover:text-text-primary">
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
          <button onClick={handleLogout} className="text-sm text-text-secondary hover:text-text-primary">
            Sign out
          </button>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-10">{children}</main>
    </div>
  );
}

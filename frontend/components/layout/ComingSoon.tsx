"use client";

import Link from "next/link";
import { PageMeta } from "@/components/layout/app-shell-context";

/** Placeholder body for nav destinations whose module hasn't been built yet. */
export function ComingSoon({ title, description }: { title: string; description?: string }) {
  return (
    <>
      <PageMeta title={title} subtitle="Coming soon" />
      <div className="mx-auto mt-16 max-w-md rounded-2xl border border-border bg-surface p-8 text-center">
        <span className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-brand/15 text-brand-light">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
            <circle cx="12" cy="12" r="9" />
            <path d="M12 7v5l3 2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </span>
        <h2 className="mt-4 text-lg font-bold text-text-primary">{title}</h2>
        <p className="mt-2 text-sm text-text-secondary">
          {description ?? "This module is on the roadmap and will appear here once it's built."}
        </p>
        <Link
          href="/dashboard"
          className="mt-6 inline-block rounded-full border border-border-strong px-4 py-2 text-sm font-semibold text-text-primary transition hover:border-brand/50"
        >
          Back to Dashboard
        </Link>
      </div>
    </>
  );
}

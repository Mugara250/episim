"use client";

import Link from "next/link";
import { Icon } from "@/components/layout/icons";
import { NotificationBell } from "@/components/layout/NotificationBell";
import { UserMenu } from "@/components/layout/UserMenu";
import { useAppShell, type StatusTone } from "@/components/layout/app-shell-context";

const TONE_DOT: Record<StatusTone, string> = {
  green: "bg-brand",
  amber: "bg-warning",
  red: "bg-error",
  slate: "bg-text-secondary",
};

export function TopBar() {
  const { header, status } = useAppShell();

  return (
    <header className="sticky top-0 z-30 border-b border-border bg-topbar/90 backdrop-blur">
      <div className="flex items-center justify-between gap-4 px-8 py-4">
        <div className="min-w-0">
          <h1 className="truncate text-xl font-bold text-text-primary">{header.title}</h1>
          {header.subtitle && (
            <p className="truncate text-sm text-text-secondary">{header.subtitle}</p>
          )}
        </div>

        <div className="flex shrink-0 items-center gap-2 sm:gap-3">
          <NotificationBell />
          <Link
            href="/settings"
            aria-label="Settings"
            className="flex h-9 w-9 items-center justify-center rounded-lg text-text-secondary transition hover:bg-surface-2 hover:text-text-primary"
          >
            <Icon name="settings" />
          </Link>

          <span className="hidden items-center gap-2 rounded-full border border-border bg-surface px-3 py-1.5 text-xs font-medium text-text-secondary md:flex">
            <span className={`h-1.5 w-1.5 rounded-full ${TONE_DOT[status.tone]}`} />
            {status.label}
          </span>

          <div className="mx-1 hidden h-8 w-px bg-border sm:block" />
          <UserMenu />
        </div>
      </div>
    </header>
  );
}

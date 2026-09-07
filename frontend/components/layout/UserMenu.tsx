"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { Icon } from "@/components/layout/icons";
import { useAppShell } from "@/components/layout/app-shell-context";
import { fullName } from "@/lib/name";
import { roleLabel } from "@/lib/roles";

function initials(first: string, last: string): string {
  return `${first.charAt(0)}${last.charAt(0)}`.toUpperCase() || "?";
}

export function UserMenu() {
  const { user, signOut } = useAppShell();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    function onClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, [open]);

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-haspopup="menu"
        aria-expanded={open}
        className="flex items-center gap-3 rounded-lg py-1 pl-1 pr-2 transition hover:bg-surface-2"
      >
        <span className="flex h-9 w-9 items-center justify-center rounded-full bg-brand/20 text-sm font-semibold text-brand-light">
          {initials(user.first_name, user.last_name)}
        </span>
        <span className="hidden text-left leading-tight sm:block">
          <span className="block text-sm font-semibold text-text-primary">{fullName(user)}</span>
          <span className="block text-xs text-text-secondary">{roleLabel(user.role)}</span>
        </span>
        <Icon name="chevron-down" width={14} height={14} className="text-text-secondary" />
      </button>

      {open && (
        <div
          role="menu"
          className="absolute right-0 z-50 mt-2 w-52 overflow-hidden rounded-xl border border-border bg-surface shadow-xl"
        >
          <div className="border-b border-border px-4 py-3 sm:hidden">
            <p className="text-sm font-semibold text-text-primary">{fullName(user)}</p>
            <p className="text-xs text-text-secondary">{roleLabel(user.role)}</p>
          </div>
          <Link
            href="/profile"
            role="menuitem"
            onClick={() => setOpen(false)}
            className="flex items-center gap-2 px-4 py-2.5 text-sm text-text-secondary transition hover:bg-surface-2 hover:text-text-primary"
          >
            <Icon name="user" width={16} height={16} />
            Profile
          </Link>
          <button
            type="button"
            role="menuitem"
            onClick={() => {
              setOpen(false);
              signOut();
            }}
            className="flex w-full items-center gap-2 px-4 py-2.5 text-left text-sm text-text-secondary transition hover:bg-surface-2 hover:text-text-primary"
          >
            <Icon name="signout" width={16} height={16} />
            Sign Out
          </button>
        </div>
      )}
    </div>
  );
}

"use client";

import { useState, type ReactNode } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Icon } from "@/components/layout/icons";
import { NAV_ITEMS, isRouteActive, type NavItem } from "@/components/layout/nav";
import { useAppShell } from "@/components/layout/app-shell-context";

function BrandMark() {
  return (
    <Link href="/dashboard" className="flex items-center gap-2.5 px-2">
      <span className="flex h-8 w-8 items-center justify-center rounded-full bg-brand text-bg">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
          <path d="M3 12h4l2 8 4-16 2 8h6" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </span>
      <span className="leading-tight">
        <span className="block text-sm font-bold text-text-primary">EpiSim</span>
        <span className="block text-[11px] text-text-secondary">Simulation System</span>
      </span>
    </Link>
  );
}

const LEAF_BASE =
  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition";
const ITEM_INACTIVE = "text-text-secondary hover:bg-surface-2 hover:text-text-primary";
const ITEM_ACTIVE = "bg-nav-active text-brand-light";

function NavLink({ href, label, icon }: { href: string; label: string; icon?: ReactNode }) {
  const pathname = usePathname();
  const active = isRouteActive(pathname, href);
  return (
    <Link href={href} className={`${LEAF_BASE} ${active ? ITEM_ACTIVE : ITEM_INACTIVE}`} aria-current={active ? "page" : undefined}>
      {icon}
      {label}
    </Link>
  );
}

function NavGroup({ item }: { item: Extract<NavItem, { kind: "group" }> }) {
  const pathname = usePathname();
  const hasActiveChild = item.children.some((c) => isRouteActive(pathname, c.href));
  const [open, setOpen] = useState(hasActiveChild);

  return (
    <div>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className={`${LEAF_BASE} w-full justify-between ${hasActiveChild ? "text-text-primary" : ITEM_INACTIVE}`}
      >
        <span className="flex items-center gap-3">
          <Icon name={item.icon} />
          {item.label}
        </span>
        <Icon
          name="chevron-down"
          width={14}
          height={14}
          className={`transition-transform ${open ? "" : "-rotate-90"}`}
        />
      </button>

      {open && (
        <div className="mt-0.5 space-y-0.5 border-l border-border pl-3 ml-5">
          {item.children.map((child) => (
            <NavLink key={child.href} href={child.href} label={child.label} />
          ))}
        </div>
      )}
    </div>
  );
}

export function Sidebar() {
  const { user, signOut } = useAppShell();

  // Role gate is real logic, not a CSS hide: admin-only groups are filtered out
  // of the rendered tree entirely for non-admins.
  const items = NAV_ITEMS.filter((item) => !(item.kind === "group" && item.adminOnly) || user.role === "admin");

  return (
    <aside className="fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-border bg-sidebar">
      <div className="px-4 py-5">
        <BrandMark />
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto px-3 pb-4">
        {items.map((item) =>
          item.kind === "link" ? (
            <NavLink key={item.href} href={item.href} label={item.label} icon={<Icon name={item.icon} />} />
          ) : (
            <NavGroup key={item.label} item={item} />
          )
        )}
      </nav>

      <div className="space-y-0.5 border-t border-border px-3 py-3">
        <NavLink href="/settings" label="Settings" icon={<Icon name="settings" />} />
        <button type="button" onClick={signOut} className={`${LEAF_BASE} w-full ${ITEM_INACTIVE}`}>
          <Icon name="signout" />
          Sign Out
        </button>
      </div>
    </aside>
  );
}

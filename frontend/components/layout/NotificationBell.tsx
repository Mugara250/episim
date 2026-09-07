"use client";

import { useEffect, useRef, useState } from "react";
import { Icon } from "@/components/layout/icons";

export type AppNotification = {
  id: string;
  title: string;
  time: string;
  read: boolean;
};

// Placeholder feed. Real wiring (fetch + mark-as-read) comes with a later
// module; the component only assumes it receives a list of notifications.
const MOCK_NOTIFICATIONS: AppNotification[] = [
  { id: "1", title: "Priority surveillance signal detected for COVID-19", time: "5 mins ago", read: false },
  { id: "2", title: "Operational status review due for COVID-19", time: "1 hour ago", read: false },
  { id: "3", title: "Data source interruption: Western Province", time: "3 hours ago", read: true },
];

export function NotificationBell({
  notifications = MOCK_NOTIFICATIONS,
}: {
  notifications?: AppNotification[];
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const unread = notifications.filter((n) => !n.read).length;

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
        aria-label={unread > 0 ? `Notifications, ${unread} unread` : "Notifications"}
        className="relative flex h-9 w-9 items-center justify-center rounded-lg text-text-secondary transition hover:bg-surface-2 hover:text-text-primary"
      >
        <Icon name="bell" />
        {unread > 0 && (
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-error ring-2 ring-topbar" />
        )}
      </button>

      {open && (
        <div className="absolute right-0 z-50 mt-2 w-80 overflow-hidden rounded-xl border border-border bg-surface shadow-xl">
          <div className="flex items-center justify-between border-b border-border px-4 py-3">
            <span className="text-sm font-semibold text-text-primary">Notifications</span>
            {unread > 0 && <span className="text-xs text-text-secondary">{unread} unread</span>}
          </div>
          <ul className="max-h-80 divide-y divide-border overflow-y-auto">
            {notifications.length === 0 && (
              <li className="px-4 py-6 text-center text-sm text-text-secondary">You&apos;re all caught up.</li>
            )}
            {notifications.map((n) => (
              <li key={n.id} className="flex gap-3 px-4 py-3">
                <span
                  className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${n.read ? "bg-text-faint" : "bg-brand"}`}
                />
                <div>
                  <p className="text-sm text-text-primary">{n.title}</p>
                  <p className="mt-0.5 text-xs text-text-secondary">{n.time}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

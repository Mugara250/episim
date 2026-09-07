"use client";

import type { ReactNode } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { TopBar } from "@/components/layout/TopBar";
import { AppShellProvider } from "@/components/layout/app-shell-context";
import type { User } from "@/lib/api";

/**
 * Persistent shell wrapped around every authenticated route (see
 * app/(app)/layout.tsx). Renders the sidebar + top bar; page content is slotted
 * into `children`. Pages set their own top-bar title via `<PageMeta />`.
 */
export function AppShell({
  user,
  onSignOut,
  children,
}: {
  user: User;
  onSignOut: () => void;
  children: ReactNode;
}) {
  return (
    <AppShellProvider user={user} signOut={onSignOut}>
      <div className="min-h-screen bg-bg">
        <Sidebar />
        <div className="flex min-h-screen flex-col pl-64">
          <TopBar />
          <main className="flex-1 px-8 py-8">{children}</main>
        </div>
      </div>
    </AppShellProvider>
  );
}

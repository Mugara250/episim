"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import type { User } from "@/lib/api";

// Different pages show different top-bar titles and connection statuses. Rather
// than each page re-implementing the top bar, the shared shell renders it and
// pages push their bits of metadata up through this context.

export type StatusTone = "green" | "amber" | "red" | "slate";

export type StatusPill = { label: string; tone: StatusTone };

export const DEFAULT_STATUS: StatusPill = { label: "Connected", tone: "green" };

type PageHeader = { title: string; subtitle?: string };

type AppShellContextValue = {
  user: User;
  signOut: () => void;
  header: PageHeader;
  status: StatusPill;
  setHeader: (header: PageHeader) => void;
  setStatus: (status: StatusPill) => void;
};

const AppShellContext = createContext<AppShellContextValue | null>(null);

export function AppShellProvider({
  user,
  signOut,
  children,
}: {
  user: User;
  signOut: () => void;
  children: ReactNode;
}) {
  const [header, setHeader] = useState<PageHeader>({ title: "" });
  const [status, setStatus] = useState<StatusPill>(DEFAULT_STATUS);

  return (
    <AppShellContext.Provider value={{ user, signOut, header, status, setHeader, setStatus }}>
      {children}
    </AppShellContext.Provider>
  );
}

export function useAppShell(): AppShellContextValue {
  const ctx = useContext(AppShellContext);
  if (!ctx) throw new Error("useAppShell must be used inside the (app) layout");
  return ctx;
}

/**
 * Drop `<PageMeta title=... />` at the top of any authenticated page to set the
 * top-bar title/subtitle (and optionally the status pill) for that route.
 */
export function PageMeta({
  title,
  subtitle,
  statusLabel,
  statusTone,
}: {
  title: string;
  subtitle?: string;
  statusLabel?: string;
  statusTone?: StatusTone;
}) {
  const { setHeader, setStatus } = useAppShell();

  useEffect(() => {
    setHeader({ title, subtitle });
  }, [title, subtitle, setHeader]);

  useEffect(() => {
    if (statusLabel) {
      setStatus({ label: statusLabel, tone: statusTone ?? "green" });
      return () => setStatus(DEFAULT_STATUS);
    }
  }, [statusLabel, statusTone, setStatus]);

  return null;
}

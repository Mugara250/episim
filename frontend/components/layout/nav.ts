import type { IconName } from "@/components/layout/icons";

// Navigation is organised around the system's four layers, not the screenshot's
// ad-hoc grouping. Each expandable group maps to one layer; leaf links map to
// modules. Only "Disease Presets" points at a real, built page today — every
// other leaf is a "Coming soon" stub until its module lands.

export type NavLeaf = { label: string; href: string };

export type NavItem =
  | { kind: "link"; label: string; href: string; icon: IconName }
  | { kind: "group"; label: string; icon: IconName; adminOnly?: boolean; children: NavLeaf[] };

export const NAV_ITEMS: NavItem[] = [
  { kind: "link", label: "Dashboard", href: "/dashboard", icon: "dashboard" },
  {
    kind: "group",
    label: "Data Management",
    icon: "data",
    children: [
      { label: "Population Data", href: "/data/population" },
      { label: "Disease Presets", href: "/disease-presets" },
      { label: "Interventions", href: "/data/interventions" },
      { label: "Healthcare Capacity", href: "/data/healthcare-capacity" },
    ],
  },
  {
    kind: "group",
    label: "Simulations",
    icon: "simulations",
    children: [
      { label: "New Simulation", href: "/simulations/new" },
      { label: "Simulation History", href: "/simulations/history" },
    ],
  },
  {
    kind: "group",
    label: "Analysis & Reporting",
    icon: "analysis",
    children: [
      { label: "Visualizations", href: "/analysis/visualizations" },
      { label: "Scenario Comparison", href: "/analysis/scenario-comparison" },
      { label: "Reports", href: "/analysis/reports" },
    ],
  },
  {
    kind: "group",
    label: "Administration",
    icon: "admin",
    adminOnly: true,
    children: [
      { label: "Users", href: "/admin/users" },
      { label: "Institutions", href: "/admin/institutions" },
      { label: "Login Activity", href: "/admin/login-activity" },
    ],
  },
];

/** True when `pathname` is `href` or a route nested beneath it. */
export function isRouteActive(pathname: string, href: string): boolean {
  return pathname === href || pathname.startsWith(`${href}/`);
}

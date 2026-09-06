import type { User } from "@/lib/api";

/**
 * UI-only mirror of the backend's app.services.permissions.can_create_presets.
 * Purely for show/hide of the "Create New Preset" button - the server is the
 * actual enforcement point (POST /disease-presets 403s regardless of this).
 */
export function canCreatePresets(user: User): boolean {
  return user.role === "admin" || (user.role === "epidemiologist" && user.has_admin_privileges);
}

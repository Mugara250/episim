export const ROLE_LABELS: Record<string, string> = {
  analyst: "Analyst",
  epidemiologist: "Epidemiologist",
  health_officer: "Health Officer",
  policy_maker: "Policy Maker",
  admin: "Administrator",
};

export function roleLabel(role: string): string {
  return ROLE_LABELS[role] ?? role;
}

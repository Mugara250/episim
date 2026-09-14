export function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="text-xs font-semibold uppercase tracking-wide text-text-secondary">{label}</span>
      <div className="mt-1.5">{children}</div>
    </label>
  );
}

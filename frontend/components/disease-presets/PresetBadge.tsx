export function PresetBadge({ isBuiltin }: { isBuiltin: boolean }) {
  return (
    <span
      className={
        "rounded-full px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide " +
        (isBuiltin ? "bg-surface-2 text-text-secondary" : "bg-brand/15 text-brand-light")
      }
    >
      {isBuiltin ? "Built-in" : "Custom"}
    </span>
  );
}

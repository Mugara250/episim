const MODULES = [
  "Registration",
  "Dashboard",
  "Population Data",
  "Disease Parameters",
  "Simulation Engine",
  "SEIR Model",
  "Agent-Based Model",
  "Interventions",
  "Geographic Spread",
  "Healthcare Capacity",
  "Visualization",
  "Scenario Compare",
  "Reports",
  "User Management",
];

const STATS = [
  { value: "14", label: "Simulation Modules" },
  { value: "5", label: "Disease Models" },
  { value: "3", label: "AI Modeling Approaches" },
  { value: "∞", label: "Scenarios Possible" },
];

export function Modules() {
  return (
    <section className="border-t border-border py-24">
      <div className="mx-auto max-w-7xl px-6">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-light">14 Modules</p>
        <h2 className="mt-4 max-w-2xl text-3xl font-bold text-text-primary md:text-4xl">
          A complete platform, purpose-built for epidemiology
        </h2>

        <div className="mt-10 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-7">
          {MODULES.map((name) => (
            <div key={name} className="rounded-xl border border-border bg-surface p-4">
              <span className="flex h-8 w-8 items-center justify-center rounded-md bg-brand/10 text-brand-light">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="9" strokeLinecap="round" />
                </svg>
              </span>
              <p className="mt-3 text-sm font-semibold text-text-primary">{name}</p>
              <p className="mt-1 text-xs text-text-secondary">Production-ready module for epidemic intelligence.</p>
            </div>
          ))}
        </div>

        <div className="mt-16 grid grid-cols-2 gap-px overflow-hidden rounded-xl border border-border bg-border md:grid-cols-4">
          {STATS.map((s) => (
            <div key={s.label} className="bg-surface px-6 py-8 text-center">
              <p className="text-3xl font-extrabold text-brand-light">{s.value}</p>
              <p className="mt-1 text-xs text-text-secondary">{s.label}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

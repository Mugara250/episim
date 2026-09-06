type Card = {
  label: string;
  title: string;
  description: string;
  gradient: string;
  span?: string;
  extra?: React.ReactNode;
};

const CARDS: Card[] = [
  {
    label: "Core Engine",
    title: "AI Simulation Engine",
    description:
      "Combines compartmental models, agent-based simulation, and network transmission synthesis. Three modeling approaches converge in a single unified prediction engine.",
    gradient: "bg-grad-teal",
    span: "md:col-span-2",
    extra: (
      <div className="mt-4 flex gap-2">
        {["SEIR", "Agent", "Network"].map((tag) => (
          <span key={tag} className="rounded-full bg-black/10 px-3 py-1 text-xs font-semibold text-ink">
            {tag}
          </span>
        ))}
      </div>
    ),
  },
  {
    label: "Spatial Analysis",
    title: "Geographic Spread",
    description: "Visualize how outbreaks propagate across regions, borders, and population centers in real time.",
    gradient: "bg-grad-purple",
  },
  {
    label: "Policy Simulation",
    title: "Intervention Scenarios",
    description: "Model lockdowns, masking, and other interventions.",
    gradient: "bg-grad-green",
    extra: (
      <div className="mt-4 space-y-2">
        {["Vaccination Campaign", "Movement Restriction"].map((item) => (
          <div key={item} className="flex items-center gap-2 rounded-full bg-black/10 px-3 py-1.5 text-xs font-medium text-ink">
            <span className="h-1.5 w-1.5 rounded-full bg-ink/70" />
            {item}
          </div>
        ))}
      </div>
    ),
  },
  {
    label: "Live Data",
    title: "Real-Time Monitoring",
    description: "Track key epidemic indicators as data streams in.",
    gradient: "bg-grad-coral",
    extra: (
      <div className="mt-4 flex gap-6">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-wide text-ink-muted">R_t Value</p>
          <p className="text-2xl font-extrabold text-ink">2.4</p>
        </div>
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-wide text-ink-muted">Doubling</p>
          <p className="text-2xl font-extrabold text-ink">9.2d</p>
        </div>
      </div>
    ),
  },
  {
    label: "Analysis Tool",
    title: "Scenario Comparison",
    description: "Compare outcomes across intervention strategies side by side.",
    gradient: "bg-grad-cyan",
    extra: (
      <div className="mt-4 flex gap-4 text-xs font-medium text-ink">
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-ink/60" /> Baseline (No Intervention)
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-ink/60" /> Vaccination + Masking
        </span>
      </div>
    ),
  },
  {
    label: "Capacity Planning",
    title: "Healthcare Capacity",
    description: "Track ICU beds, general wards, and ventilator availability against projected demand.",
    gradient: "bg-grad-amber",
    extra: (
      <div className="mt-4 space-y-2">
        {[
          ["ICU Beds", 67],
          ["General Wards", 45],
          ["Ventilators", 41],
        ].map(([label, pct]) => (
          <div key={label as string}>
            <div className="mb-1 flex justify-between text-[11px] font-semibold text-ink">
              <span>{label}</span>
              <span>{pct}%</span>
            </div>
            <div className="h-1.5 rounded-full bg-black/10">
              <div className="h-1.5 rounded-full bg-ink/70" style={{ width: `${pct}%` }} />
            </div>
          </div>
        ))}
      </div>
    ),
  },
  {
    label: "Access Control",
    title: "Role-Based Access",
    description: "Tailored dashboards for each team member.",
    gradient: "bg-grad-pink",
    extra: (
      <div className="mt-4">
        <div className="flex -space-x-2">
          {["Ep", "PH", "An", "Cl"].map((initials) => (
            <span key={initials} className="flex h-8 w-8 items-center justify-center rounded-full border-2 border-white/40 bg-black/10 text-[10px] font-bold text-ink">
              {initials}
            </span>
          ))}
          <span className="flex h-8 w-8 items-center justify-center rounded-full border-2 border-white/40 bg-black/10 text-[10px] font-bold text-ink">
            +5
          </span>
        </div>
        <p className="mt-2 text-xs text-ink-muted">Epidemiologist · Policy Maker · etc</p>
      </div>
    ),
  },
  {
    label: "Data Export",
    title: "Reporting & Export",
    description: "One-click reports in your preferred format. Shareable links for stakeholder collaboration.",
    gradient: "bg-grad-green",
  },
];

export function Features() {
  return (
    <section id="tools" className="mx-auto max-w-7xl px-6 py-24">
      <div className="mx-auto max-w-2xl rounded-2xl border border-border bg-surface/60 py-10 text-center">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-light">Platform Features</p>
        <h2 className="mt-4 px-6 text-3xl font-bold text-text-primary md:text-4xl">
          Every tool a health analyst needs — in one simulation platform
        </h2>
      </div>

      <div className="mt-10 grid gap-4 md:grid-cols-3">
        {CARDS.map((card) => (
          <div
            key={card.title}
            className={`text-ink rounded-2xl p-6 ${card.gradient} ${card.span ?? ""}`}
          >
            <p className="text-[11px] font-semibold uppercase tracking-wider text-ink-muted">{card.label}</p>
            <h3 className="mt-2 text-xl font-bold text-ink">{card.title}</h3>
            <p className="mt-2 text-sm text-ink-muted">{card.description}</p>
            {card.extra}
          </div>
        ))}
      </div>
    </section>
  );
}

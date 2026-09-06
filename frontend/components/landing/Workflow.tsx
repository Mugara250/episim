const STEPS = [
  {
    step: "1",
    title: "Configure",
    description:
      "Upload census data and policy briefs, calibrate your model inputs. EpiSim connects to WHO and other health registries.",
  },
  {
    step: "2",
    title: "Simulate",
    description: "Run powerful scenarios using built-in agent-based and network models computed in parallel. Results in seconds.",
  },
  {
    step: "3",
    title: "Decide",
    description: "Share live results and visual dashboards with team members and non-technical stakeholders. Evidence-based decisions, faster.",
  },
];

export function Workflow() {
  return (
    <section className="border-t border-border py-24">
      <div className="mx-auto max-w-4xl px-6 text-center">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-light">Workflow</p>
        <h2 className="mt-4 text-3xl font-bold text-text-primary md:text-4xl">From data to decision in three steps</h2>

        <div className="mt-16 grid gap-12 md:grid-cols-3">
          {STEPS.map((s) => (
            <div key={s.step}>
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full border border-brand/40 bg-surface text-lg font-bold text-brand-light">
                {s.step}
              </div>
              <h3 className="mt-4 text-lg font-bold text-text-primary">{s.title}</h3>
              <p className="mt-2 text-sm text-text-secondary">{s.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

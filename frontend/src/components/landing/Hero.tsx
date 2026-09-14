import { Button } from "@/components/Button";

function SeirChart() {
  return (
    <div className="relative rounded-2xl border border-border bg-surface p-5 shadow-2xl shadow-black/40">
      <div className="absolute -top-3 left-5 rounded-md border border-border bg-surface-2 px-2.5 py-1 text-xs font-mono text-text-secondary">
        R<sub>0</sub> = <span className="text-brand-light font-semibold">2.4</span>
      </div>

      <div className="mb-4 flex items-center justify-between pt-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-text-secondary">
          SEIR Model · Live Projection
        </span>
        <span className="flex items-center gap-1.5 text-xs text-brand-light">
          <span className="h-1.5 w-1.5 rounded-full bg-brand animate-pulse" />
          Running
        </span>
      </div>

      <svg viewBox="0 0 400 180" className="w-full" role="img" aria-label="SEIR model projection chart">
        {[40, 80, 120, 160].map((y) => (
          <line key={y} x1="0" y1={y} x2="400" y2={y} stroke="#1E2836" strokeDasharray="4 4" />
        ))}
        <path d="M0,30 C80,40 120,90 160,120 C220,150 300,165 400,168" fill="none" stroke="#38BDF8" strokeWidth="2.5" />
        <path d="M0,170 C60,168 100,140 150,90 C190,55 230,45 280,55 C330,65 370,90 400,110" fill="none" stroke="#FB6B6B" strokeWidth="2.5" />
        <path d="M0,175 C80,174 130,160 170,120 C210,80 250,65 300,68 C340,70 370,80 400,90" fill="none" stroke="#F5B942" strokeWidth="2.5" />
        <path d="M0,178 C100,177 160,170 200,140 C260,95 320,50 400,20" fill="none" stroke="#12D6A0" strokeWidth="2.5" />
      </svg>

      <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] text-text-secondary">
        <LegendDot color="#38BDF8" label="Susceptible (8K)" />
        <LegendDot color="#F5B942" label="Exposed (1K)" />
        <LegendDot color="#FB6B6B" label="Infectious (2K)" />
        <LegendDot color="#12D6A0" label="Recovered (6K)" />
      </div>

      <div className="pointer-events-none absolute right-4 top-16 rounded-lg border border-border bg-surface-2 px-3 py-1.5 text-xs text-text-secondary shadow-lg">
        <span className="h-1.5 w-1.5 rounded-full bg-brand inline-block mr-1.5" />
        3 Active scenarios
      </div>
      <div className="pointer-events-none absolute bottom-16 left-8 rounded-lg border border-border bg-surface-2 px-3 py-1.5 text-xs text-text-secondary shadow-lg">
        Day <span className="font-semibold text-text-primary">49</span> · <span className="text-brand-light">Projection</span>
      </div>
    </div>
  );
}

function LegendDot({ color, label }: { color: string; label: string }) {
  return (
    <span className="flex items-center gap-1.5">
      <span className="h-2 w-2 rounded-sm" style={{ backgroundColor: color }} />
      {label}
    </span>
  );
}

export function Hero() {
  return (
    <section className="mx-auto grid max-w-7xl gap-12 px-6 py-20 md:grid-cols-2 md:items-center md:py-28">
      <div>
        <span className="inline-flex items-center gap-2 rounded-full border border-border bg-surface px-3 py-1.5 text-xs font-medium text-brand-light">
          <span className="h-1.5 w-1.5 rounded-full bg-brand" />
          Epidemic Intelligence · Active
        </span>

        <h1 className="mt-6 text-6xl font-extrabold leading-[1.05] tracking-tight text-text-faint md:text-7xl">
          Predict.
          <br />
          <span className="text-brand-light">Prepare.</span>
          <br />
          Protect.
        </h1>

        <p className="mt-6 max-w-md text-base text-text-secondary">
          AI-driven epidemic simulation for public health authorities in developing countries — built on SEIR,
          agent-based, and network transmission models.
        </p>

        <div className="mt-8 flex flex-wrap gap-4">
          <Button href="/register">
            Start Simulation
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M5 12h14M13 6l6 6-6 6" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </Button>
          <Button variant="secondary" href="#tools">
            Watch Demo
          </Button>
        </div>
      </div>

      <SeirChart />
    </section>
  );
}

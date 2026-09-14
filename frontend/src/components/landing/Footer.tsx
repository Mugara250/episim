const COLUMNS = [
  {
    title: "Platform",
    links: ["Documentation", "API Reference", "Simulation Engine", "Changelog", "Status"],
  },
  {
    title: "Organization",
    links: ["About EpiSim", "Research Papers", "Careers", "Support", "Contact"],
  },
  {
    title: "Legal",
    links: ["Privacy Policy", "Terms of Use", "Data Security", "Accessibility"],
  },
];

export function Footer() {
  return (
    <footer className="border-t border-border">
      <div className="mx-auto max-w-7xl px-6 py-16">
        <div className="grid gap-10 md:grid-cols-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand text-bg">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M3 12h4l2 8 4-16 2 8h6" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </span>
              <span className="text-lg font-bold text-text-primary">EpiSim</span>
            </div>
            <p className="mt-4 max-w-xs text-sm text-text-secondary">
              AI-driven epidemic simulation for public health authorities in developing countries. Built to protect
              communities before outbreaks become crises.
            </p>
          </div>

          {COLUMNS.map((col) => (
            <div key={col.title}>
              <p className="text-xs font-semibold uppercase tracking-wider text-text-secondary">{col.title}</p>
              <ul className="mt-4 space-y-3">
                {col.links.map((link) => (
                  <li key={link}>
                    <a href="#" className="text-sm text-text-secondary transition hover:text-text-primary">
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-16 flex flex-col items-center justify-between gap-4 border-t border-border pt-8 text-xs text-text-secondary md:flex-row">
          <p>&copy; 2026 EpiSim — for public health professionals in developing countries.</p>
          <p>Epidemic Intelligence · African Market · Open Science</p>
        </div>
      </div>
    </footer>
  );
}

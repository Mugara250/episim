import Link from "next/link";

const LINKS = [
  { label: "Why", href: "#why" },
  { label: "Tools", href: "#tools" },
  { label: "Cases", href: "#cases" },
  { label: "Pricing", href: "#pricing" },
  { label: "Docs", href: "#docs" },
];

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-border bg-bg/80 backdrop-blur">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <Link href="/" className="flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand text-bg">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M3 12h4l2 8 4-16 2 8h6" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </span>
          <span className="text-lg font-bold tracking-tight text-text-primary">EpiSim</span>
        </Link>

        <div className="hidden items-center gap-8 md:flex">
          {LINKS.map((link) => (
            <a key={link.label} href={link.href} className="text-sm text-text-secondary transition hover:text-text-primary">
              {link.label}
            </a>
          ))}
        </div>

        <div className="flex items-center gap-4">
          <span className="hidden items-center gap-2 rounded-full border border-border bg-surface px-3 py-1.5 text-xs text-brand-light lg:flex">
            <span className="h-1.5 w-1.5 rounded-full bg-brand" />
            AI-Powered Epidemic Simulation
          </span>
          <Link href="/login" className="text-sm text-text-secondary transition hover:text-text-primary">
            Sign in
          </Link>
          <Link
            href="/register"
            className="rounded-full bg-brand px-4 py-2 text-sm font-semibold text-bg transition hover:bg-brand-light"
          >
            Get Started
          </Link>
        </div>
      </nav>
    </header>
  );
}

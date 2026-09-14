// Generic institution archetypes, not real organizations — the prototype's
// trust bar reused specific real logos, which would misrepresent an
// unaffiliated academic prototype as endorsed by them.
const PARTNERS = ["Ministry of Health", "Regional Health Authority", "National Biomedical Institute", "Global Health Alliance"];

export function TrustBar() {
  return (
    <section className="border-y border-border bg-surface/40 py-10">
      <div className="mx-auto max-w-7xl px-6 text-center">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-light">
          Trusted by public health institutions across Sub-Saharan Africa
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-x-12 gap-y-6">
          {PARTNERS.map((name) => (
            <span key={name} className="text-lg font-bold text-text-secondary/70">
              {name}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}

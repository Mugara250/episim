import type { Metadata } from "next";
import { Syne } from "next/font/google";
import "./globals.css";

// next/font self-hosts the font at build time and injects it via a CSS
// variable - this avoids the invalid-CSS-position problem you get from a
// manual `@import url(...)` placed after `@tailwind` directives (an
// `@import` must be the very first rule in a stylesheet, so once Tailwind
// expands into real rules ahead of it, browsers silently drop it).
const syne = Syne({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
  variable: "--font-syne",
  display: "swap",
});

export const metadata: Metadata = {
  title: "EpiSim — AI-Driven Epidemic Simulation",
  description: "AI-driven epidemic simulation for public health authorities in developing countries.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={syne.variable}>
      <body className="bg-bg text-text-primary antialiased">{children}</body>
    </html>
  );
}

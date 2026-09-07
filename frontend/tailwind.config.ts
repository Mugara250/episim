import type { Config } from "tailwindcss";

// Palette extracted from the Magic Patterns landing page prototype
// (dark navy ground, vivid emerald brand, gradient accent cards).
const config: Config = {
  darkMode: ["class"],
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0A0E16",
        surface: "#0F1828",
        "surface-2": "#121A28",
        // Persistent app shell surfaces (slightly distinct from content panels).
        sidebar: "#0B111C",
        topbar: "#0A0E16",
        "nav-active": "rgba(16, 185, 129, 0.12)",
        border: "#1E293B",
        "border-strong": "#2A3647",
        "text-primary": "#F1F5F9",
        "text-secondary": "#94A3B8",
        "text-faint": "#334155",
        brand: {
          DEFAULT: "#10B981",
          dark: "#0EA57D",
          light: "#5EEAC2",
        },
        success: "#10B981",
        warning: "#F5B942",
        error: "#FB6B6B",
        info: "#38D9E8",
        ink: "#0F172A",
        "ink-muted": "rgba(15, 23, 42, 0.65)",
      },
      fontFamily: {
        sans: ["var(--font-syne)", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      backgroundImage: {
        "grad-teal": "linear-gradient(135deg, #2FE0B9, #0EA57D)",
        "grad-purple": "linear-gradient(135deg, #C4A6FA, #8B5CF6)",
        "grad-green": "linear-gradient(135deg, #86EFAC, #22C55E)",
        "grad-coral": "linear-gradient(135deg, #FDA4AF, #F43F5E)",
        "grad-cyan": "linear-gradient(135deg, #67E8F9, #06B6D4)",
        "grad-amber": "linear-gradient(135deg, #FDE68A, #F59E0B)",
        "grad-pink": "linear-gradient(135deg, #F9A8D4, #EC4899)",
      },
    },
  },
  plugins: [],
};

export default config;

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { AuthHeader } from "@/components/auth/AuthHeader";
import { PasswordInput } from "@/components/auth/PasswordInput";
import { Field } from "@/components/Field";
import { login } from "@/lib/api";
import { saveSession } from "@/lib/auth";

const DEMO_EMAIL = "demo@episim.dev";
const DEMO_PASSWORD = "Demo1234!";

const ROLE_HOME: Record<string, string> = {
  admin: "/dashboard",
  analyst: "/dashboard",
  epidemiologist: "/dashboard",
  health_officer: "/dashboard",
  policy_maker: "/dashboard",
};

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(true);
  const [showDemo, setShowDemo] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const result = await login(email, password);
      saveSession(result.access_token, result.role, remember);
      router.push(ROLE_HOME[result.role] ?? "/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-16">
      <div className="w-full max-w-md">
        <AuthHeader title="Welcome back" subtitle="Sign in to your account" />

        <div className="mt-6 text-center">
          <button
            type="button"
            onClick={() => setShowDemo((v) => !v)}
            className="text-sm font-medium text-brand-light hover:underline"
          >
            Show demo credentials
          </button>
          {showDemo && (
            <div className="mt-3 rounded-lg border border-border bg-surface px-4 py-3 text-left text-xs text-text-secondary">
              <p>
                Email: <span className="text-text-primary">{DEMO_EMAIL}</span>
              </p>
              <p>
                Password: <span className="text-text-primary">{DEMO_PASSWORD}</span>
              </p>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <Field label="Email address">
            <input
              type="email"
              required
              placeholder="you@institution.org"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input"
            />
          </Field>

          <Field label="Password">
            <PasswordInput
              value={password}
              onChange={setPassword}
              placeholder="Enter your password"
              autoComplete="current-password"
            />
          </Field>

          <div className="flex items-center justify-between text-sm">
            <label className="flex items-center gap-2 text-text-secondary">
              <input
                type="checkbox"
                checked={remember}
                onChange={(e) => setRemember(e.target.checked)}
                className="h-4 w-4 rounded border-border bg-surface accent-brand"
              />
              Remember me
            </label>
            <Link href="/forgot-password" className="text-brand-light hover:underline">
              Forgot password?
            </Link>
          </div>

          {error && <p className="text-sm text-error">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-brand px-4 py-3 text-sm font-bold text-white transition hover:bg-brand-light disabled:opacity-50"
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-text-secondary">
          Don&apos;t have an account?{" "}
          <Link href="/register" className="font-medium text-brand-light hover:underline">
            Register
          </Link>
        </p>
      </div>
    </main>
  );
}

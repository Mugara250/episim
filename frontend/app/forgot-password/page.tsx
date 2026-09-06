"use client";

import { useState } from "react";
import Link from "next/link";
import { AuthHeader } from "@/components/auth/AuthHeader";
import { Field } from "@/components/Field";
import { forgotPassword } from "@/lib/api";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await forgotPassword(email);
      setSent(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  if (sent) {
    return (
      <main className="flex min-h-screen items-center justify-center px-6">
        <div className="w-full max-w-md text-center">
          <h1 className="text-2xl font-bold text-text-primary">Check your email</h1>
          <p className="mt-3 text-sm text-text-secondary">
            If an account exists for <span className="text-text-primary">{email}</span>, we&apos;ve sent a password
            reset link. In local dev, open Mailhog at{" "}
            <span className="text-brand-light">localhost:8025</span> to view it.
          </p>
          <Link href="/login" className="mt-6 inline-block text-sm font-medium text-brand-light hover:underline">
            Back to sign in
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-16">
      <div className="w-full max-w-md">
        <AuthHeader title="Forgot password" subtitle="We'll email you a link to reset it" />

        <form onSubmit={handleSubmit} className="mt-8 space-y-4">
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

          {error && <p className="text-sm text-error">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-full bg-brand px-4 py-3 text-sm font-bold text-bg transition hover:bg-brand-light disabled:opacity-50"
          >
            {loading ? "Sending..." : "Send reset link"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-text-secondary">
          Remembered it?{" "}
          <Link href="/login" className="font-medium text-brand-light hover:underline">
            Sign In
          </Link>
        </p>
      </div>
    </main>
  );
}

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { AuthHeader } from "@/components/auth/AuthHeader";
import { PasswordInput } from "@/components/auth/PasswordInput";
import { Field } from "@/components/Field";
import { getInstitutions, register, type Institution, type RegisterInput } from "@/lib/api";

const ROLES: { value: RegisterInput["role"]; label: string }[] = [
  { value: "analyst", label: "Analyst" },
  { value: "epidemiologist", label: "Epidemiologist" },
  { value: "health_officer", label: "Health Officer" },
  { value: "policy_maker", label: "Policy Maker" },
  { value: "admin", label: "Admin" },
];

export default function RegisterPage() {
  const router = useRouter();
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [institutionId, setInstitutionId] = useState("");
  const [role, setRole] = useState<RegisterInput["role"]>("analyst");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [agreed, setAgreed] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getInstitutions()
      .then(setInstitutions)
      .catch(() => setInstitutions([]));
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    if (!agreed) {
      setError("You must agree to the Terms of Service and Privacy Policy");
      return;
    }

    setLoading(true);
    try {
      await register({
        first_name: firstName,
        last_name: lastName,
        email,
        password,
        role,
        institution_id: institutionId || undefined,
        is_active: true,
        is_superuser: false,
        is_verified: false,
      });
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  if (success) {
    return (
      <main className="flex min-h-screen items-center justify-center px-6">
        <div className="w-full max-w-md text-center">
          <h1 className="text-2xl font-bold text-text-primary">Check your email</h1>
          <p className="mt-3 text-sm text-text-secondary">
            We sent a verification link to <span className="text-text-primary">{email}</span>. In local dev, open
            Mailhog at <span className="text-brand-light">localhost:8025</span> to view it.
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
        <AuthHeader title="Create your account" subtitle="Join the global epidemic preparedness network" />

        <form onSubmit={handleSubmit} className="mt-8 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Field label="First name">
              <input
                required
                placeholder="Jane"
                autoComplete="given-name"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="input"
              />
            </Field>
            <Field label="Last name">
              <input
                required
                placeholder="Doe"
                autoComplete="family-name"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className="input"
              />
            </Field>
          </div>

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

          <Field label="Institution">
            <select value={institutionId} onChange={(e) => setInstitutionId(e.target.value)} className="input">
              <option value="">Select your institution</option>
              {institutions.map((inst) => (
                <option key={inst.id} value={inst.id}>
                  {inst.name}
                </option>
              ))}
            </select>
          </Field>

          <Field label="Role">
            <select
              value={role}
              onChange={(e) => setRole(e.target.value as RegisterInput["role"])}
              className="input"
            >
              {ROLES.map((r) => (
                <option key={r.value} value={r.value}>
                  {r.label}
                </option>
              ))}
            </select>
          </Field>

          <Field label="Password">
            <PasswordInput
              value={password}
              onChange={setPassword}
              placeholder="Create a strong password"
              autoComplete="new-password"
            />
          </Field>

          <Field label="Confirm password">
            <PasswordInput
              value={confirmPassword}
              onChange={setConfirmPassword}
              placeholder="Re-enter your password"
              autoComplete="new-password"
            />
          </Field>

          <label className="flex items-start gap-2 text-sm text-text-secondary">
            <input
              type="checkbox"
              checked={agreed}
              onChange={(e) => setAgreed(e.target.checked)}
              className="mt-0.5 h-4 w-4 rounded border-border bg-surface accent-brand"
            />
            <span>
              I agree to the{" "}
              <Link href="#" className="text-brand-light hover:underline">
                Terms of Service
              </Link>{" "}
              and{" "}
              <Link href="#" className="text-brand-light hover:underline">
                Privacy Policy
              </Link>
            </span>
          </label>

          {error && <p className="text-sm text-error">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-brand px-4 py-3 text-sm font-bold text-white transition hover:bg-brand-dark disabled:opacity-50"
          >
            {loading ? "Creating account..." : "Create Account"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-text-secondary">
          Already have an account?{" "}
          <Link href="/login" className="font-medium text-brand-light hover:underline">
            Sign In
          </Link>
        </p>
      </div>
    </main>
  );
}

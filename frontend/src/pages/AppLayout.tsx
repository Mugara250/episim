import { useEffect, useState } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import { AppShell } from "@/components/layout/AppShell";
import { getMe, type User } from "@/lib/api";
import { clearSession, getToken } from "@/lib/auth";

// Shared layout for every authenticated route, rendered as a React Router
// layout route so page content is slotted in via <Outlet /> instead of
// Next's implicit children rendering.
export default function AppLayout() {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [redirecting, setRedirecting] = useState(false);

  useEffect(() => {
    if (!getToken()) {
      setRedirecting(true);
      navigate("/login", { replace: true });
      return;
    }
    getMe()
      .then(setUser)
      .catch(() => {
        clearSession();
        setRedirecting(true);
        navigate("/login", { replace: true });
      });
  }, [navigate]);

  function signOut() {
    clearSession();
    navigate("/login", { replace: true });
  }

  if (!user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-bg text-sm text-text-secondary">
        {redirecting ? "Redirecting to sign in…" : "Loading…"}
      </div>
    );
  }

  return (
    <AppShell user={user} onSignOut={signOut}>
      <Outlet />
    </AppShell>
  );
}

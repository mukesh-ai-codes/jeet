"use client";

/**
 * ProtectedRoute — wraps an authenticated page.
 *
 * Behavior:
 *   - status === "loading"  → render a tiny spinner
 *   - status === "unauthenticated" → redirect to /login
 *   - wrong role → redirect to user's own dashboard
 *   - not onboarded → redirect to onboarding (unless allowDuringOnboarding)
 *   - all clear → render children
 */

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { dashboardPathFor, isAllowedOnPath, landingPathFor } from "@/lib/routes";
import type { UserRole } from "@/types";

type Props = {
  allowedRoles: UserRole[];
  children: React.ReactNode;
  allowDuringOnboarding?: boolean;
};

function CenteredSpinner() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-white">
      <div className="flex flex-col items-center gap-3">
        <div className="h-8 w-8 rounded-full border-2 border-indigo-200 border-t-indigo-600 animate-spin" />
        <p className="text-sm text-slate-500">Loading…</p>
      </div>
    </div>
  );
}

export default function ProtectedRoute({
  allowedRoles,
  children,
  allowDuringOnboarding = false,
}: Props) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, status, isLoading } = useAuth();

  useEffect(() => {
    if (isLoading) return;

    if (status === "unauthenticated" || !user) {
      router.replace("/login");
      return;
    }

    if (!isAllowedOnPath(user, allowedRoles)) {
      router.replace(dashboardPathFor(user.role));
      return;
    }

    if (!allowDuringOnboarding && !user.is_onboarded) {
      router.replace(landingPathFor(user));
      return;
    }
  }, [status, user, isLoading, allowedRoles, allowDuringOnboarding, router, pathname]);

  if (isLoading || !user) return <CenteredSpinner />;
  if (!isAllowedOnPath(user, allowedRoles)) return <CenteredSpinner />;
  if (!allowDuringOnboarding && !user.is_onboarded) return <CenteredSpinner />;

  return <>{children}</>;
}

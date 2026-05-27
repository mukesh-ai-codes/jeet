/**
 * useAuth — the only hook UI components should use to access auth state.
 *
 * On first mount of any consumer, this hook kicks off a /api/auth/me check
 * to validate any token in localStorage. Subsequent consumers reuse the
 * cached result.
 *
 * Usage:
 *   const { user, status, login, logout } = useAuth();
 *   if (status === "loading") return <Spinner />;
 *   if (!user) return <SignInPrompt />;
 *   return <div>Hi, {user.full_name}</div>;
 */

import { useEffect } from "react";
import { useAuthStore } from "@/store/auth";
import { authApi } from "@/lib/api";
import type { LoginRequest } from "@/types";

let hasBootedOnce = false;

export function useAuth() {
  const user = useAuthStore((s) => s.user);
  const status = useAuthStore((s) => s.status);
  const setSession = useAuthStore((s) => s.setSession);
  const refreshFromServer = useAuthStore((s) => s.refreshFromServer);
  const logout = useAuthStore((s) => s.logout);
  const markOnboarded = useAuthStore((s) => s.markOnboarded);

  // Boot once per page load. Subsequent renders skip this.
  useEffect(() => {
    if (!hasBootedOnce) {
      hasBootedOnce = true;
      refreshFromServer();
    }
  }, [refreshFromServer]);

  async function login(payload: LoginRequest) {
    const response = await authApi.login(payload);
    setSession(response);
    return response.user;
  }

  async function completeOnboarding() {
    const response = await authApi.completeOnboarding();
    setSession(response);
    markOnboarded();
    return response.user;
  }

  return {
    user,
    status,
    isAuthenticated: status === "authenticated",
    isLoading: status === "loading",
    login,
    logout,
    completeOnboarding,
  };
}

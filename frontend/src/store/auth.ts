/**
 * Auth store (Zustand).
 *
 * Single source of truth for: who's logged in, what their JWT is, and
 * whether we're still checking. UI components subscribe via useAuth hook.
 *
 * State machine:
 *   status = "loading"        — initial mount, validating a stored token
 *   status = "unauthenticated" — no token or invalid token
 *   status = "authenticated"   — token + user object both present
 */

import { create } from "zustand";
import { authApi, clearToken, getToken, setToken } from "@/lib/api";
import type { AuthUser, LoginResponse } from "@/types";

type AuthStatus = "loading" | "authenticated" | "unauthenticated";

type AuthState = {
  user: AuthUser | null;
  status: AuthStatus;

  // Actions
  setSession: (response: LoginResponse) => void;
  refreshFromServer: () => Promise<void>;
  logout: () => void;
  markOnboarded: () => void;
};

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  status: "loading",

  /**
   * Called after a successful /api/auth/login or /api/auth/complete-onboarding.
   * Stores the token AND updates the in-memory user.
   */
  setSession: (response) => {
    setToken(response.access_token);
    set({ user: response.user, status: "authenticated" });
  },

  /**
   * Called on app boot. If a token exists in localStorage, validate it by
   * fetching /api/auth/me. If it's valid, hydrate the store. If it's expired
   * or invalid, clear it and mark unauthenticated.
   */
  refreshFromServer: async () => {
    const token = getToken();
    if (!token) {
      set({ user: null, status: "unauthenticated" });
      return;
    }

    try {
      const user = await authApi.me();
      set({ user, status: "authenticated" });
    } catch {
      clearToken();
      set({ user: null, status: "unauthenticated" });
    }
  },

  /**
   * Called from a logout button or after the API interceptor clears the token.
   */
  logout: () => {
    clearToken();
    set({ user: null, status: "unauthenticated" });
  },

  /**
   * Optimistic UI update after onboarding completes — flips is_onboarded to
   * true in the in-memory user without refetching.
   */
  markOnboarded: () => {
    const current = get().user;
    if (current) {
      set({ user: { ...current, is_onboarded: true } });
    }
  },
}));

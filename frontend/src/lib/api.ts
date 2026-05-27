/**
 * JEET API Client
 *
 * Centralized axios instance for talking to the FastAPI backend.
 * Handles auth tokens, base URL, and response interceptors.
 *
 * Direct token helpers (getToken / setToken / clearToken) are exported
 * for use by the auth store. UI components should NOT call these directly;
 * they should use the useAuth hook instead.
 */

import axios, { AxiosError, AxiosInstance } from "axios";
import type { AuthUser, LoginRequest, LoginResponse } from "@/types";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const TOKEN_KEY = "jeet_access_token";

// -------- Token helpers --------

export const getToken = (): string | null => {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
};

export const setToken = (token: string): void => {
  if (typeof window !== "undefined") {
    localStorage.setItem(TOKEN_KEY, token);
  }
};

export const clearToken = (): void => {
  if (typeof window !== "undefined") {
    localStorage.removeItem(TOKEN_KEY);
  }
};

// -------- Axios instance --------

export const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 15_000,
});

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const status = error.response?.status;
    const requestUrl = error.config?.url || "";
    const isAuthAttempt =
      requestUrl.includes("/api/auth/login") ||
      requestUrl.includes("/api/auth/token");

    if (status === 401 && !isAuthAttempt && typeof window !== "undefined") {
      clearToken();
      if (!window.location.pathname.startsWith("/login")) {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

// -------- Error helper --------

export const getErrorMessage = (err: unknown): string => {
  if (axios.isAxiosError(err)) {
    return (
      (err.response?.data as { detail?: string })?.detail ||
      err.message ||
      "An unexpected error occurred"
    );
  }
  return "An unexpected error occurred";
};

// -------- Auth API --------

export const authApi = {
  async login(payload: LoginRequest): Promise<LoginResponse> {
    const { data } = await api.post<LoginResponse>("/api/auth/login", payload);
    return data;
  },

  async me(): Promise<AuthUser> {
    const { data } = await api.get<AuthUser>("/api/auth/me");
    return data;
  },

  async completeOnboarding(): Promise<LoginResponse> {
    const { data } = await api.post<LoginResponse>(
      "/api/auth/complete-onboarding"
    );
    return data;
  },
};

// -------- Onboarding API --------

export type AdminConfigurePayload = {
  institute_name: string;
  institute_size: "1-2" | "3-5" | "6-15" | "16-50" | "50+";
  primary_exams: Array<"JEE" | "NEET" | "Foundation" | "Other">;
  cohort_count: number;
  mentor_count: number;
  review_tool_today:
    | "spreadsheets"
    | "whatsapp"
    | "lms"
    | "nothing_structured";
  biggest_pain:
    | "silent_dropouts"
    | "low_engagement"
    | "parent_anxiety"
    | "mentor_overload"
    | "revenue_leakage";
  go_live_window: "this_week" | "this_month" | "exploring";
  notes?: string;
};

export const onboardingApi = {
  async configureAdmin(payload: AdminConfigurePayload) {
    const { data } = await api.post("/api/onboarding/admin/configure", payload);
    return data;
  },
};

"use client";

/**
 * useStudentDashboard — fetches all data needed for /student in parallel.
 *
 * Returns:
 *   { data: { dashboard, plan, weakChapters, streak }, loading, error, refresh }
 *
 * All four endpoints are fetched concurrently via Promise.allSettled. If
 * any fail we still surface the partial data we DID get, plus an error.
 */

import { useCallback, useEffect, useState } from "react";

import { studentApi, getErrorMessage } from "@/lib/api";
import type {
  StudentDashboard,
  DailyPlanResponse,
  WeakChaptersResponse,
  StreakResponse,
} from "@/types";

type DashboardState = {
  dashboard: StudentDashboard | null;
  plan: DailyPlanResponse | null;
  weakChapters: WeakChaptersResponse | null;
  streak: StreakResponse | null;
};

type UseStudentDashboardReturn = {
  data: DashboardState;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
};

export function useStudentDashboard(): UseStudentDashboardReturn {
  const [data, setData] = useState<DashboardState>({
    dashboard: null,
    plan: null,
    weakChapters: null,
    streak: null,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    setError(null);

    const [dashRes, planRes, weakRes, streakRes] = await Promise.allSettled([
      studentApi.getDashboard(),
      studentApi.getDailyPlan(),
      studentApi.getWeakChapters(),
      studentApi.getStreak(),
    ]);

    const next: DashboardState = {
      dashboard: dashRes.status === "fulfilled" ? dashRes.value : null,
      plan: planRes.status === "fulfilled" ? planRes.value : null,
      weakChapters: weakRes.status === "fulfilled" ? weakRes.value : null,
      streak: streakRes.status === "fulfilled" ? streakRes.value : null,
    };

    let firstError: string | null = null;
    if (dashRes.status === "rejected") {
      firstError = `Dashboard: ${getErrorMessage(dashRes.reason)}`;
    } else if (planRes.status === "rejected") {
      firstError = `Daily plan: ${getErrorMessage(planRes.reason)}`;
    } else if (weakRes.status === "rejected") {
      firstError = `Weak chapters: ${getErrorMessage(weakRes.reason)}`;
    } else if (streakRes.status === "rejected") {
      firstError = `Streak: ${getErrorMessage(streakRes.reason)}`;
    }

    setData(next);
    setError(firstError);
    setLoading(false);
  }, []);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  return {
    data,
    loading,
    error,
    refresh: fetchAll,
  };
}

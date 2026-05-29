"use client";

/**
 * Command Center data hook — parallel-fetches the four analytics endpoints
 * the admin dashboard leads with. Uses Promise.allSettled so one slow/failing
 * endpoint never blanks the whole page (same resilience pattern as the
 * student + mentor dashboards).
 */

import { useEffect, useState } from "react";
import { getToken, API_BASE_URL } from "@/lib/api";

export interface AdminOverview {
  total_students: number;
  active_subscriptions: number;
  churned_subscriptions: number;
  retention_pct: number;
  total_revenue_crore: number;
  total_revenue_inr: number;
  payment_success_rate: number;
}

export interface RevenueByPlan {
  plan_name: string;
  plan_slug: string;
  subscribers: number;
  total_revenue_inr: number;
  avg_revenue_per_user: number;
}
export interface RevenueData {
  by_plan: RevenueByPlan[];
  total_captured_inr: number;
  total_failed_attempts_inr: number;
}

export interface ChurnReason {
  primary_reason: string;
  student_count: number;
  percentage: number;
}
export interface ChurnData {
  total_churned: number;
  breakdown: ChurnReason[];
}

export interface InterventionType {
  intervention_type: string;
  total_count: number;
  successful_count: number;
  no_response_count: number;
  failed_count: number;
  success_rate: number;
  avg_risk_reduction: number;
}
export interface InterventionData {
  total_interventions: number;
  overall_success_rate: number;
  by_type: InterventionType[];
}

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  if (!res.ok) throw new Error(`${path} -> ${res.status}`);
  return res.json();
}

export function useAdminOverview() {
  const [overview, setOverview] = useState<AdminOverview | null>(null);
  const [revenue, setRevenue] = useState<RevenueData | null>(null);
  const [churn, setChurn] = useState<ChurnData | null>(null);
  const [interventions, setInterventions] = useState<InterventionData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;
    (async () => {
      const [o, r, c, i] = await Promise.allSettled([
        fetchJson<AdminOverview>("/api/admin/overview"),
        fetchJson<RevenueData>("/api/admin/revenue"),
        fetchJson<ChurnData>("/api/admin/analytics/churn-reasons"),
        fetchJson<InterventionData>("/api/admin/interventions/effectiveness"),
      ]);
      if (!alive) return;
      if (o.status === "fulfilled") setOverview(o.value);
      if (r.status === "fulfilled") setRevenue(r.value);
      if (c.status === "fulfilled") setChurn(c.value);
      if (i.status === "fulfilled") setInterventions(i.value);
      setLoading(false);
    })();
    return () => { alive = false; };
  }, []);

  return { overview, revenue, churn, interventions, loading };
}

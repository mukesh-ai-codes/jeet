/**
 * Day-13 helper: derive a risk tier client-side from dashboard data.
 *
 * The backend `v_student_features` view computes a real risk tier with 47
 * signals, but `/api/students/me/dashboard` doesn't yet expose it.
 *
 * Day 16 polish should:
 *   1. Add `risk_tier: str` to StudentDashboard Pydantic schema
 *   2. Surface it in the dashboard endpoint query
 *   3. Replace calls to deriveRisk() with `dashboard.risk_tier` directly
 *
 * Until then this gives a directionally-correct tier from signals we already
 * have. Conservative on the urgent end — we'd rather under-flag than have a
 * student see "URGENT" on a friendly home screen.
 */

import type { StudentDashboard } from "@/types";

export type RiskTier = "stable" | "watch" | "critical" | "urgent" | "lost";

export function deriveRisk(dashboard: StudentDashboard | null): RiskTier {
  if (!dashboard) return "stable";

  const eng = dashboard.engagement;
  const learn = dashboard.learning;
  const asses = dashboard.assessments;

  if (dashboard.enrollment.status === "churned") return "lost";

  // Urgent — major recent disengagement or score collapse
  if (eng.days_since_last_login > 7) return "urgent";
  if (asses.recent_avg_score_pct > 0 && asses.recent_avg_score_pct < 35) return "urgent";

  // Critical — moderate slipping
  if (eng.days_since_last_login > 3) return "critical";
  if (learn.attendance_rate < 0.5 && learn.sessions_scheduled > 0) return "critical";

  // Watch — early warning
  if (asses.recent_avg_score_pct > 0 && asses.recent_avg_score_pct < 50) return "watch";
  if (learn.lesson_completion_rate < 0.4 && learn.lessons_started > 5) return "watch";

  return "stable";
}

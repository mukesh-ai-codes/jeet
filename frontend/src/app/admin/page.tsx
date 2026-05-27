"use client";

import {
  BarChart3,
  LineChart,
  Users,
  Wallet,
  Activity,
  Bell,
} from "lucide-react";

import ProtectedRoute from "@/components/auth/ProtectedRoute";
import AppShell from "@/components/app/AppShell";
import PlaceholderPanel from "@/components/app/PlaceholderPanel";

export default function AdminDashboardPage() {
  return (
    <ProtectedRoute allowedRoles={["admin"]}>
      <AppShell>
        <PlaceholderPanel
          badge="Command Center"
          title="Welcome to your retention OS."
          subtitle="Your workspace is active. The Command Center surfaces institute-wide health: cohort retention, churn breakdowns, revenue forecasting, intervention effectiveness. Real data lands on Day 15."
          shipsOn="Day 15"
          modules={[
            {
              icon: LineChart,
              name: "Cohort retention curves",
              description:
                "Week-over-week retention per cohort with side-by-side comparisons across programs and mentors.",
            },
            {
              icon: BarChart3,
              name: "Churn-reason breakdown",
              description:
                "Why students are leaving — academic, financial, engagement, peer, family — segmented by cohort.",
            },
            {
              icon: Wallet,
              name: "Revenue health",
              description:
                "Captured vs failed payments, renewal probability, at-risk LTV per cohort. Forecast 90 days out.",
            },
            {
              icon: Activity,
              name: "Intervention effectiveness",
              description:
                "Which mentor playbooks are saving students. A/B-tested results across cohorts and risk tiers.",
            },
            {
              icon: Users,
              name: "Mentor capacity & load",
              description:
                "Who's overloaded, who has slack, who needs back-up. Reassign students before mentors burn out.",
            },
            {
              icon: Bell,
              name: "Daily alert digest",
              description:
                "One morning email summarizing every urgent and critical student across your institute.",
            },
          ]}
        />
      </AppShell>
    </ProtectedRoute>
  );
}

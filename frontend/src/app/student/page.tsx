"use client";

import { BookOpen, Sparkles, Flame } from "lucide-react";

import ProtectedRoute from "@/components/auth/ProtectedRoute";
import AppShell from "@/components/app/AppShell";
import PlaceholderPanel from "@/components/app/PlaceholderPanel";

export default function StudentDashboardPage() {
  return (
    <ProtectedRoute allowedRoles={["student"]}>
      <AppShell>
        <PlaceholderPanel
          badge="Student Workspace"
          title="Your study home, simplified."
          subtitle="Your dashboard surfaces today's lessons, your weakest chapters, and your AI tutor Tara — all in one place. Real workspace lands on Day 13."
          shipsOn="Day 13"
          modules={[
            {
              icon: BookOpen,
              name: "Today's lessons",
              description:
                "Personalized lesson recommendations based on your weak chapters and recent assessment dips.",
            },
            {
              icon: Sparkles,
              name: "Meet Tara",
              description:
                "Your NCERT-grounded AI tutor — three modes (Saathi, Strategist, Guru) and 80+ Indian-context analogies.",
            },
            {
              icon: Flame,
              name: "Engagement streak",
              description:
                "Track your daily study streak, time-on-platform, and progress against your exam-day plan.",
            },
          ]}
        />
      </AppShell>
    </ProtectedRoute>
  );
}

"use client";

import { Heart, MessageCircle, TrendingUp } from "lucide-react";

import ProtectedRoute from "@/components/auth/ProtectedRoute";
import AppShell from "@/components/app/AppShell";
import PlaceholderPanel from "@/components/app/PlaceholderPanel";

export default function ParentDashboardPage() {
  return (
    <ProtectedRoute allowedRoles={["parent"]}>
      <AppShell>
        <PlaceholderPanel
          badge="Parent View"
          title="How your child is doing."
          subtitle="Encouragement-first dashboard. Less panic, more clarity. You'll see study trends, mentor notes, and exam readiness — not raw scores. Ships Day 14."
          shipsOn="Day 14"
          modules={[
            {
              icon: TrendingUp,
              name: "Weekly progress",
              description:
                "What your child worked on, where they improved, what they're focusing on next week.",
            },
            {
              icon: Heart,
              name: "Mentor notes",
              description:
                "Brief, supportive updates from your child's mentor. Designed to reassure, not alarm.",
            },
            {
              icon: MessageCircle,
              name: "When to step in",
              description:
                "JEET tells you when a quick word from you matters — and stays quiet when it doesn't.",
            },
          ]}
        />
      </AppShell>
    </ProtectedRoute>
  );
}

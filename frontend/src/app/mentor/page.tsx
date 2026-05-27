"use client";

import { LayoutDashboard, MessageSquare, Sparkles } from "lucide-react";

import ProtectedRoute from "@/components/auth/ProtectedRoute";
import AppShell from "@/components/app/AppShell";
import PlaceholderPanel from "@/components/app/PlaceholderPanel";

export default function MentorDashboardPage() {
  return (
    <ProtectedRoute allowedRoles={["mentor"]}>
      <AppShell>
        <PlaceholderPanel
          badge="Coach Console"
          title="Your daily at-risk queue."
          subtitle="JEET's mentor view sorts your students by risk every morning, surfaces exactly why each one is slipping, and gives you the intervention playbook that's worked for similar students. Real queue ships Day 15."
          shipsOn="Day 15"
          modules={[
            {
              icon: LayoutDashboard,
              name: "At-risk queue (ranked)",
              description:
                "Today's students who need you, sorted by risk score. Hover for the 47 signals behind each score.",
            },
            {
              icon: Sparkles,
              name: "Whisper Layer",
              description:
                "Plain-English intervention recommendations — what to say, when to call, what worked before.",
            },
            {
              icon: MessageSquare,
              name: "Intervention log",
              description:
                "Log every conversation. JEET tracks outcomes so you see which approaches actually save students.",
            },
          ]}
        />
      </AppShell>
    </ProtectedRoute>
  );
}

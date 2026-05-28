"use client";

import { useState } from "react";
import { Loader2 } from "lucide-react";

import ProtectedRoute from "@/components/auth/ProtectedRoute";
import AppShell from "@/components/app/AppShell";
import MentorSummaryStrip from "@/components/mentor/MentorSummaryStrip";
import AtRiskQueue from "@/components/mentor/AtRiskQueue";
import StudentDetailDrawer from "@/components/mentor/StudentDetailDrawer";

import { useAuth } from "@/hooks/useAuth";
import { useMentorConsole } from "@/hooks/useMentorConsole";
import type { AtRiskStudent, StudentWhisperResponse } from "@/types";

export default function MentorConsolePage() {
  return (
    <ProtectedRoute allowedRoles={["mentor"]}>
      <AppShell>
        <MentorContent />
      </AppShell>
    </ProtectedRoute>
  );
}

function MentorContent() {
  const { user } = useAuth();
  const { cohorts, queue, loading, error, getWhisper, refresh } = useMentorConsole();
  const firstName = user?.full_name?.split(" ")[0] || "there";

  const [active, setActive] = useState<AtRiskStudent | null>(null);
  const [whisper, setWhisper] = useState<StudentWhisperResponse | null>(null);
  const [whisperLoading, setWhisperLoading] = useState(false);

  async function openStudent(s: AtRiskStudent) {
    setActive(s);
    setWhisper(null);
    setWhisperLoading(true);
    const data = await getWhisper(s.student_user_id);
    setWhisper(data);
    setWhisperLoading(false);
  }

  function closeDrawer() {
    setActive(null);
    setWhisper(null);
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <Loader2 className="h-7 w-7 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Greeting */}
      <div>
        <p className="text-sm font-semibold text-indigo-600">Coach Console</p>
        <h1 className="mt-1 font-display text-2xl md:text-3xl font-bold text-slate-900">
          Good to see you, {firstName}.
        </h1>
        <p className="mt-1 text-sm text-slate-600">
          JEET watched your students overnight. Here&apos;s who needs you today.
        </p>
      </div>

      {error && (
        <div className="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          {error}
        </div>
      )}

      <MentorSummaryStrip queue={queue} cohorts={cohorts} />

      <AtRiskQueue queue={queue} onOpen={openStudent} />

      <StudentDetailDrawer
        student={active}
        whisper={whisper}
        whisperLoading={whisperLoading}
        onClose={closeDrawer}
        onLogged={refresh}
      />
    </div>
  );
}

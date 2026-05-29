"use client";

import ProtectedRoute from "@/components/auth/ProtectedRoute";
import AppShell from "@/components/app/AppShell";
import WelcomeHeader from "@/components/student/WelcomeHeader";
import TodayPlan from "@/components/student/TodayPlan";
import TaraTeaser from "@/components/student/TaraTeaser";
import RecentAssessments from "@/components/student/RecentAssessments";
import CohortCard from "@/components/student/CohortCard";
import EngagementSnapshot from "@/components/student/EngagementSnapshot";
import WeakChaptersList from "@/components/student/WeakChaptersList";
import DashboardSkeleton from "@/components/student/DashboardSkeleton";

import { useAuth } from "@/hooks/useAuth";
import { useStudentDashboard } from "@/hooks/useStudentDashboard";
import { softenTierForStudent } from "@/lib/riskDerive";

export default function StudentDashboardPage() {
  return (
    <ProtectedRoute allowedRoles={["student"]}>
      <AppShell>
        <DashboardContent />
      </AppShell>
    </ProtectedRoute>
  );
}

function DashboardContent() {
  const { user } = useAuth();
  const { data, loading, error } = useStudentDashboard();

  if (loading) {
    return <DashboardSkeleton />;
  }

  const firstName = user?.full_name?.split(" ")[0] || "there";
  const riskTier = softenTierForStudent(data.dashboard?.risk_tier);
  const streakDays = data.streak?.current_streak ?? null;

  return (
    <div className="space-y-10">
      <WelcomeHeader
        firstName={firstName}
        streakDays={streakDays}
        riskTier={riskTier}
      />

      {error && (
        <div className="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          Some data couldn't load: {error}. Showing what we have.
        </div>
      )}

      {/* HERO — today's plan */}
      <section>
        <div className="mb-4">
          <h2 className="font-display text-xl font-bold text-slate-900">
            Today's plan
          </h2>
          <p className="text-sm text-slate-600">
            AI-picked from your weak subjects, lesson sequence, and recent
            scores.
          </p>
        </div>
        <TodayPlan items={data.plan?.items || []} />
      </section>

      {/* Tara teaser */}
      <TaraTeaser />

      {/* Below-the-fold sections */}
      {data.dashboard && (
        <>
          <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <RecentAssessments
                assessments={data.dashboard.recent_assessments}
              />
            </div>
            <CohortCard
              enrollment={data.dashboard.enrollment}
              profile={data.dashboard.profile}
            />
          </section>

          <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <EngagementSnapshot
              engagement={data.dashboard.engagement}
              learning={data.dashboard.learning}
            />
            <WeakChaptersList
              chapters={data.weakChapters?.weak_chapters || []}
            />
          </section>
        </>
      )}
    </div>
  );
}

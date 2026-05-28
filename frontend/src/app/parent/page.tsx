"use client";

import { Loader2 } from "lucide-react";

import ProtectedRoute from "@/components/auth/ProtectedRoute";
import AppShell from "@/components/app/AppShell";
import ChildPicker from "@/components/parent/ChildPicker";
import ParentStatTiles from "@/components/parent/ParentStatTiles";
import MentorCard from "@/components/parent/MentorCard";
import StepInPanel from "@/components/parent/StepInPanel";
import PositiveHighlights from "@/components/parent/PositiveHighlights";

import { useAuth } from "@/hooks/useAuth";
import { useParentDashboard } from "@/hooks/useParentDashboard";

export default function ParentDashboardPage() {
  return (
    <ProtectedRoute allowedRoles={["parent"]}>
      <AppShell>
        <ParentContent />
      </AppShell>
    </ProtectedRoute>
  );
}

function ParentContent() {
  const { user } = useAuth();
  const {
    children,
    selectedChildId,
    selectChild,
    dashboard,
    childrenLoading,
    dashboardLoading,
    error,
  } = useParentDashboard();

  const parentFirstName = user?.full_name?.split(" ")[0] || "there";

  if (childrenLoading) {
    return (
      <div className="flex items-center justify-center py-24">
        <Loader2 className="h-7 w-7 animate-spin text-indigo-600" />
      </div>
    );
  }

  if (children.length === 0) {
    return (
      <div className="max-w-md mx-auto mt-16 rounded-2xl border border-slate-200 bg-white p-8 text-center">
        <h2 className="font-display text-lg font-bold text-slate-900">
          No children linked yet
        </h2>
        <p className="mt-2 text-sm text-slate-600">
          Once your institute links your child's account, their progress will
          appear here. Reach out to your coaching institute to get set up.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Greeting */}
      <div>
        <p className="text-sm font-semibold text-indigo-600">
          Parent view
        </p>
        <h1 className="mt-1 font-display text-2xl md:text-3xl font-bold text-slate-900">
          Hi {parentFirstName}, here's how things are going.
        </h1>
      </div>

      {/* Child picker */}
      <ChildPicker
        children={children}
        selectedId={selectedChildId}
        onSelect={selectChild}
      />

      {error && (
        <div className="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          Couldn't load the dashboard: {error}
        </div>
      )}

      {/* Dashboard body */}
      {dashboardLoading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="h-6 w-6 animate-spin text-indigo-600" />
        </div>
      ) : dashboard ? (
        <div className="space-y-8">
          {/* Stat tiles */}
          <ParentStatTiles data={dashboard} />

          {/* What's going well — encouragement-first */}
          <PositiveHighlights insights={dashboard.insights} />

          {/* When to step in — silent unless action needed */}
          <StepInPanel
            insights={dashboard.insights}
            childFirstName={dashboard.child_name.split(" ")[0]}
          />

          {/* Mentor card — calm "on track" or real intervention history */}
          <MentorCard
            mentor={dashboard.mentor}
            interventions={dashboard.recent_interventions}
            childFirstName={dashboard.child_name.split(" ")[0]}
          />
        </div>
      ) : null}
    </div>
  );
}

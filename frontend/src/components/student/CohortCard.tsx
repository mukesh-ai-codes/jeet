"use client";

/**
 * CohortCard — student's enrollment and program info.
 *
 * Data: dashboard.enrollment + dashboard.profile
 *
 * Shows program name, cohort name, mentor name, target exam, days active.
 */

import { Users, Award, Calendar, Target, MessageSquare } from "lucide-react";
import type { StudentDashboard } from "@/types";

const TARGET_EXAM_LABEL: Record<string, string> = {
  jee_main: "JEE Main",
  jee_advanced: "JEE Advanced",
  neet_ug: "NEET UG",
  foundation: "Foundation",
  board: "Boards",
};

export default function CohortCard({
  enrollment,
  profile,
}: {
  enrollment: StudentDashboard["enrollment"];
  profile: StudentDashboard["profile"];
}) {
  const targetExamLabel = profile.target_exam
    ? TARGET_EXAM_LABEL[profile.target_exam] || profile.target_exam
    : "Not set";

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest text-indigo-600">
            Your cohort
          </p>
          <h3 className="mt-1 font-display text-lg font-bold text-slate-900">
            {enrollment.program_name}
          </h3>
        </div>
        <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-semibold text-emerald-700 ring-1 ring-inset ring-emerald-200 uppercase tracking-widest">
          {enrollment.status}
        </span>
      </div>

      <div className="mt-5 space-y-3.5">
        {enrollment.cohort_name && (
          <Row icon={Users} label="Cohort" value={enrollment.cohort_name} />
        )}
        {enrollment.mentor_name && (
          <Row
            icon={MessageSquare}
            label="Mentor"
            value={enrollment.mentor_name}
          />
        )}
        <Row icon={Target} label="Targeting" value={targetExamLabel} />
        <Row
          icon={Calendar}
          label="Days active"
          value={`${enrollment.days_active} days`}
        />
        {profile.grade && (
          <Row icon={Award} label="Grade" value={`Class ${profile.grade}`} />
        )}
      </div>
    </div>
  );
}

function Row({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Users;
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-start gap-3">
      <Icon className="h-3.5 w-3.5 text-slate-400 mt-0.5 shrink-0" />
      <div className="min-w-0 flex-1">
        <p className="text-xs text-slate-500">{label}</p>
        <p className="text-sm font-medium text-slate-900 truncate">{value}</p>
      </div>
    </div>
  );
}

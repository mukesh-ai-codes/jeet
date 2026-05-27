"use client";

/**
 * RecentAssessments — table of the student's most recent assessments.
 *
 * Data: dashboard.recent_assessments (array of RecentAssessment)
 *
 * Each row: title (with subject chip), score % with color, date.
 * Empty state: friendly nudge if no assessments yet.
 */

import { FileText, ArrowRight } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import type { StudentDashboard } from "@/types";

function scoreToneClass(pct: number): string {
  if (pct >= 75) return "text-emerald-700 bg-emerald-50 ring-emerald-200";
  if (pct >= 55) return "text-amber-700 bg-amber-50 ring-amber-200";
  return "text-red-700 bg-red-50 ring-red-200";
}

export default function RecentAssessments({
  assessments,
}: {
  assessments: StudentDashboard["recent_assessments"];
}) {
  if (!assessments || assessments.length === 0) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-6">
        <h3 className="font-display text-base font-semibold text-slate-900">
          Recent assessments
        </h3>
        <div className="mt-6 text-center py-8">
          <FileText className="h-8 w-8 text-slate-300 mx-auto" />
          <p className="mt-3 text-sm text-slate-500">
            No assessments yet. Your scores will appear here once you take one.
          </p>
        </div>
      </div>
    );
  }

  const recent = assessments.slice(0, 5);

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6">
      <div className="flex items-end justify-between mb-5">
        <h3 className="font-display text-base font-semibold text-slate-900">
          Recent assessments
        </h3>
        <span className="text-xs text-slate-500">Last {recent.length}</span>
      </div>

      <div className="divide-y divide-slate-100">
        {recent.map((a, i) => {
          const pct = Math.round(a.percentage);
          return (
            <div
              key={i}
              className="flex items-center justify-between gap-4 py-3 first:pt-0 last:pb-0"
            >
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-slate-900 truncate">
                  {a.title}
                </p>
                <p className="text-xs text-slate-500 mt-0.5">
                  {a.subject}
                  {a.chapter ? ` · ${a.chapter}` : ""}
                  {" · "}
                  {formatDistanceToNow(new Date(a.submitted_at), { addSuffix: true })}
                </p>
              </div>
              <span
                className={`shrink-0 rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset ${scoreToneClass(pct)}`}
              >
                {pct}%
              </span>
            </div>
          );
        })}
      </div>

      {assessments.length > 5 && (
        <button
          type="button"
          className="mt-4 inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-700"
        >
          View all {assessments.length} assessments
          <ArrowRight className="h-3 w-3" />
        </button>
      )}
    </div>
  );
}

"use client";

/**
 * EngagementSnapshot — 4 key engagement/learning stats with a small viz.
 *
 * Data: dashboard.engagement + dashboard.learning
 *
 * Shows:
 *   - Unique active days (engagement)
 *   - Lesson completion rate (learning) — with a progress bar
 *   - Attendance rate (learning)
 *   - Days since last login (engagement) — colored
 */

import { TrendingUp, BookOpen, CalendarCheck, Clock } from "lucide-react";
import type { StudentDashboard } from "@/types";

function staleColor(daysSinceLogin: number): string {
  if (daysSinceLogin <= 1) return "text-emerald-700";
  if (daysSinceLogin <= 3) return "text-amber-700";
  return "text-red-700";
}

export default function EngagementSnapshot({
  engagement,
  learning,
}: {
  engagement: StudentDashboard["engagement"];
  learning: StudentDashboard["learning"];
}) {
  const completionPct = Math.round((learning.lesson_completion_rate || 0) * 100);
  const attendancePct = Math.round((learning.attendance_rate || 0) * 100);

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6">
      <h3 className="font-display text-base font-semibold text-slate-900">
        Engagement snapshot
      </h3>
      <p className="text-xs text-slate-500 mt-1">Your week-by-week pattern</p>

      <div className="mt-5 grid grid-cols-2 gap-4">
        <StatTile
          icon={TrendingUp}
          label="Active days"
          value={engagement.unique_active_days}
          sublabel="total"
        />
        <StatTile
          icon={Clock}
          label="Last login"
          value={engagement.days_since_last_login}
          sublabel={engagement.days_since_last_login === 1 ? "day ago" : "days ago"}
          valueClass={staleColor(engagement.days_since_last_login)}
        />
        <StatTile
          icon={CalendarCheck}
          label="Attendance"
          value={`${attendancePct}%`}
          sublabel={`${learning.sessions_attended}/${learning.sessions_scheduled} sessions`}
        />
        <StatTile
          icon={BookOpen}
          label="Lessons done"
          value={learning.lessons_completed}
          sublabel={`of ${learning.lessons_started} started`}
        />
      </div>

      {/* Completion bar */}
      <div className="mt-6">
        <div className="flex items-center justify-between mb-2">
          <p className="text-xs font-medium text-slate-700">Lesson completion rate</p>
          <p className="text-xs font-semibold text-slate-900">{completionPct}%</p>
        </div>
        <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-indigo-600 rounded-full transition-all"
            style={{ width: `${Math.min(100, Math.max(0, completionPct))}%` }}
          />
        </div>
      </div>
    </div>
  );
}

function StatTile({
  icon: Icon,
  label,
  value,
  sublabel,
  valueClass = "text-slate-900",
}: {
  icon: typeof TrendingUp;
  label: string;
  value: string | number;
  sublabel: string;
  valueClass?: string;
}) {
  return (
    <div className="rounded-lg border border-slate-100 bg-slate-50 p-3">
      <div className="flex items-center gap-1.5 text-xs text-slate-500">
        <Icon className="h-3 w-3" />
        {label}
      </div>
      <div className={`mt-1.5 font-display text-xl font-bold ${valueClass}`}>
        {value}
      </div>
      <div className="text-[10px] text-slate-500 mt-0.5">{sublabel}</div>
    </div>
  );
}

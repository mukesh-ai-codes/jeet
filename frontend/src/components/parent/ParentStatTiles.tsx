"use client";

/**
 * ParentStatTiles — 4 headline numbers, framed for parents.
 *
 * Data: ParentDashboard
 *
 * Deliberately warm framing:
 *   - Attendance as "X of Y sessions" feel, here as a clean %
 *   - Last active colored (green recent, red stale)
 *   - Lessons completion as a friendly %
 *   - Days active as tenure
 */

import { CalendarCheck, Clock, BookOpen, TrendingUp } from "lucide-react";
import type { ParentDashboard } from "@/types";

function lastActiveLabel(days: number): { text: string; tone: string } {
  if (days <= 0) return { text: "Today", tone: "text-emerald-700" };
  if (days === 1) return { text: "Yesterday", tone: "text-emerald-700" };
  if (days <= 3) return { text: `${days} days ago`, tone: "text-amber-700" };
  return { text: `${days} days ago`, tone: "text-red-700" };
}

export default function ParentStatTiles({ data }: { data: ParentDashboard }) {
  const attendancePct = Math.round(data.attendance_rate * 100);
  const completionPct = Math.round(data.lesson_completion_rate * 100);
  const lastActive = lastActiveLabel(data.days_since_last_login);

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <Tile
        icon={CalendarCheck}
        label="Class attendance"
        value={`${attendancePct}%`}
        sublabel="of live sessions"
        tone="text-slate-900"
      />
      <Tile
        icon={Clock}
        label="Last active"
        value={lastActive.text}
        sublabel="on the platform"
        tone={lastActive.tone}
      />
      <Tile
        icon={BookOpen}
        label="Lessons done"
        value={`${completionPct}%`}
        sublabel="of assigned work"
        tone="text-slate-900"
      />
      <Tile
        icon={TrendingUp}
        label="With the cohort"
        value={`${data.days_active}`}
        sublabel="days and counting"
        tone="text-slate-900"
      />
    </div>
  );
}

function Tile({
  icon: Icon,
  label,
  value,
  sublabel,
  tone,
}: {
  icon: typeof Clock;
  label: string;
  value: string;
  sublabel: string;
  tone: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5">
      <div className="flex items-center gap-1.5 text-xs text-slate-500">
        <Icon className="h-3.5 w-3.5" />
        {label}
      </div>
      <div className={`mt-2 font-display text-2xl font-bold ${tone}`}>
        {value}
      </div>
      <div className="text-xs text-slate-500 mt-0.5">{sublabel}</div>
    </div>
  );
}

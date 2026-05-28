"use client";

/**
 * AtRiskRow — one student in the mentor's triage queue.
 *
 * Renders the "3-signal why" derived from backend fields. The signals are
 * picked deterministically per student so the most-explanatory ones show.
 */

import { ChevronRight, Calendar, BookX, AlertTriangle, TrendingDown } from "lucide-react";
import type { AtRiskStudent } from "@/types";
import RiskBadge from "./RiskBadge";

function signalsFor(s: AtRiskStudent): { icon: typeof Calendar; text: string; tone: string }[] {
  const out: { icon: typeof Calendar; text: string; tone: string }[] = [];

  if (s.days_since_last_login >= 7) {
    out.push({
      icon: Calendar,
      text: `${s.days_since_last_login}d since login`,
      tone: "text-red-600",
    });
  }
  if (s.avg_score_pct > 0 && s.avg_score_pct < 50) {
    out.push({
      icon: TrendingDown,
      text: `${Math.round(s.avg_score_pct)}% avg score`,
      tone: "text-orange-600",
    });
  }
  if (s.attendance_rate < 0.7 && s.attendance_rate > 0) {
    out.push({
      icon: AlertTriangle,
      text: `${Math.round(s.attendance_rate * 100)}% attendance`,
      tone: "text-amber-600",
    });
  }
  if (s.failed_assessments >= 3) {
    out.push({
      icon: BookX,
      text: `${s.failed_assessments} failed quizzes`,
      tone: "text-orange-600",
    });
  }
  if (s.lesson_completion_rate < 0.4) {
    out.push({
      icon: BookX,
      text: `${Math.round(s.lesson_completion_rate * 100)}% lessons done`,
      tone: "text-amber-600",
    });
  }
  if (s.failed_payments > 0) {
    out.push({
      icon: AlertTriangle,
      text: `${s.failed_payments} payment failed`,
      tone: "text-red-600",
    });
  }

  return out.slice(0, 3);
}

const EXAM_LABEL: Record<string, string> = {
  jee_main: "JEE Main",
  jee_advanced: "JEE Adv",
  neet_ug: "NEET",
  foundation: "Foundation",
  board: "Boards",
};

export default function AtRiskRow({
  student,
  onOpen,
}: {
  student: AtRiskStudent;
  onOpen: (s: AtRiskStudent) => void;
}) {
  const signals = signalsFor(student);
  const initials = student.full_name
    .split(" ")
    .map((n) => n[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <button
      type="button"
      onClick={() => onOpen(student)}
      className="w-full text-left flex items-center gap-4 px-5 py-4 hover:bg-slate-50 transition group"
    >
      {/* Avatar */}
      <div className="h-10 w-10 rounded-full bg-indigo-100 text-indigo-700 text-sm font-bold flex items-center justify-center shrink-0">
        {initials}
      </div>

      {/* Identity */}
      <div className="min-w-0 w-44 md:w-56">
        <p className="text-sm font-semibold text-slate-900 truncate">{student.full_name}</p>
        <p className="text-xs text-slate-500 truncate">
          Class {student.grade} · {EXAM_LABEL[student.target_exam] || student.target_exam}
        </p>
      </div>

      {/* Signals */}
      <div className="hidden md:flex flex-1 flex-wrap gap-x-4 gap-y-1">
        {signals.map((sig, i) => {
          const Icon = sig.icon;
          return (
            <span key={i} className={`inline-flex items-center gap-1 text-xs ${sig.tone}`}>
              <Icon className="h-3 w-3" />
              {sig.text}
            </span>
          );
        })}
      </div>

      {/* Risk + chevron */}
      <div className="ml-auto flex items-center gap-3 shrink-0">
        <RiskBadge tier={student.risk_tier} score={student.risk_score} />
        <ChevronRight className="h-4 w-4 text-slate-400 group-hover:text-slate-700" />
      </div>
    </button>
  );
}

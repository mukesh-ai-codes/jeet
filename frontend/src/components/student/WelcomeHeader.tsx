"use client";

/**
 * WelcomeHeader — first thing the student sees on /student.
 *
 * Shows:
 *   - Time-based greeting (Good morning / afternoon / evening)
 *   - Student's first name
 *   - Risk tier chip + streak badge (small, supplementary)
 */

import { Flame } from "lucide-react";
import RiskChip from "./RiskChip";

function timeGreeting(): string {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 17) return "Good afternoon";
  if (h < 21) return "Good evening";
  return "Good evening";
}

type Props = {
  firstName: string;
  riskTier?: string | null;
  streakDays?: number | null;
};

export default function WelcomeHeader({ firstName, riskTier, streakDays }: Props) {
  return (
    <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
      <div>
        <p className="text-sm font-semibold text-indigo-600">
          Your AI-powered study workspace
        </p>
        <h1 className="mt-1 font-display text-3xl md:text-4xl font-bold text-slate-900 leading-tight">
          {timeGreeting()}, {firstName} 👋
        </h1>
        <p className="mt-1 text-sm text-slate-600">
          Here's what JEET picked for you today.
        </p>
      </div>

      <div className="flex items-center gap-3 shrink-0">
        {typeof streakDays === "number" && streakDays > 0 && (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-orange-50 px-2.5 py-1 text-xs font-semibold text-orange-700 ring-1 ring-inset ring-orange-200">
            <Flame className="h-3 w-3" />
            {streakDays}-day streak
          </span>
        )}
        <RiskChip tier={riskTier} />
      </div>
    </div>
  );
}

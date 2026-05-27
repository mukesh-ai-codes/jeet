"use client";

/**
 * TodayPlan — renders the 3-slot AI-picked plan from /daily-plan.
 *
 * Each slot card shows:
 *   - Slot label and icon (review / learn / practice)
 *   - Subject + chapter line
 *   - Lesson title (large, clickable)
 *   - Personalized reason (driven by backend logic)
 *   - Duration + difficulty pills
 *   - "Start lesson" button -> /student/lesson/[id] (Phase 5)
 *
 * If a slot is missing (e.g. fresh student has no weak subject yet), the
 * card silently isn't rendered. The hero header still appears with whatever
 * items we do have.
 */

import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  RefreshCw,
  GraduationCap,
  Sparkles,
  Clock,
  ArrowRight,
  Layers,
} from "lucide-react";
import type { DailyPlanItem, DailyPlanSlot } from "@/types";

const SLOT_META: Record<DailyPlanSlot, {
  icon: typeof RefreshCw;
  iconBg: string;
  iconColor: string;
  accentBorder: string;
}> = {
  review: {
    icon: RefreshCw,
    iconBg: "bg-amber-50",
    iconColor: "text-amber-600",
    accentBorder: "hover:border-amber-300",
  },
  learn: {
    icon: GraduationCap,
    iconBg: "bg-indigo-50",
    iconColor: "text-indigo-600",
    accentBorder: "hover:border-indigo-300",
  },
  practice: {
    icon: Sparkles,
    iconBg: "bg-emerald-50",
    iconColor: "text-emerald-600",
    accentBorder: "hover:border-emerald-300",
  },
};

const DIFFICULTY_LABEL: Record<number, string> = {
  1: "Easy",
  2: "Easy",
  3: "Moderate",
  4: "Hard",
  5: "Hard",
};

function PlanCard({ item }: { item: DailyPlanItem }) {
  const meta = SLOT_META[item.slot];
  const Icon = meta.icon;

  return (
    <Link
      href={`/student/lesson/${item.lesson.id}`}
      className={`block rounded-2xl border border-slate-200 bg-white p-5 transition hover:shadow-md ${meta.accentBorder}`}
    >
      <div className="flex items-start justify-between">
        <div className={`rounded-lg p-2 ${meta.iconBg}`}>
          <Icon className={`h-5 w-5 ${meta.iconColor}`} />
        </div>
        <span className="text-[10px] font-semibold uppercase tracking-widest text-slate-400">
          {item.slot}
        </span>
      </div>

      <p className="mt-4 text-xs font-semibold text-slate-500">{item.label}</p>
      <h3 className="mt-1 font-display text-lg font-bold text-slate-900 leading-snug line-clamp-2">
        {item.lesson.title}
      </h3>
      <p className="mt-1 text-xs text-slate-500">
        {item.lesson.subject_name} · {item.lesson.chapter}
      </p>

      <p className="mt-3 text-sm text-slate-600 leading-relaxed line-clamp-2">
        {item.reason}
      </p>

      <div className="mt-4 flex items-center justify-between">
        <div className="flex items-center gap-3 text-xs text-slate-500">
          <span className="inline-flex items-center gap-1">
            <Clock className="h-3 w-3" />
            {item.lesson.duration_minutes} min
          </span>
          <span className="inline-flex items-center gap-1">
            <Layers className="h-3 w-3" />
            {DIFFICULTY_LABEL[item.lesson.difficulty_level] || "Moderate"}
          </span>
        </div>
        <span className="inline-flex items-center text-xs font-semibold text-indigo-600">
          Start
          <ArrowRight className="h-3 w-3 ml-1" />
        </span>
      </div>
    </Link>
  );
}

export default function TodayPlan({ items }: { items: DailyPlanItem[] }) {
  if (items.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center">
        <p className="text-sm text-slate-600">
          Your personalized plan will appear here as you complete more
          assessments and lessons.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {items.map((item) => (
        <PlanCard key={item.slot} item={item} />
      ))}
    </div>
  );
}

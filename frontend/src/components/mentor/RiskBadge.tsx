"use client";

import type { RiskTier } from "@/types";

// Solid, well-separated severity ramp so tiers are scannable down a long queue.
// urgent = red (alarm) · critical = amber/orange · watch = yellow · stable = green.
const STYLES: Record<RiskTier, { bg: string; text: string; ring: string; dot: string; label: string }> = {
  urgent:   { bg: "bg-red-600",    text: "text-white",       ring: "ring-red-700",     dot: "bg-red-200",     label: "Urgent" },
  critical: { bg: "bg-amber-500",  text: "text-white",       ring: "ring-amber-600",   dot: "bg-amber-100",   label: "Critical" },
  watch:    { bg: "bg-yellow-200", text: "text-yellow-900",  ring: "ring-yellow-400",  dot: "bg-yellow-600",  label: "Watch" },
  stable:   { bg: "bg-emerald-100",text: "text-emerald-800", ring: "ring-emerald-300", dot: "bg-emerald-600", label: "Stable" },
  lost:     { bg: "bg-slate-200",  text: "text-slate-700",   ring: "ring-slate-400",   dot: "bg-slate-500",   label: "Lost" },
};

export default function RiskBadge({ tier, score }: { tier: RiskTier; score?: number }) {
  const s = STYLES[tier] || STYLES.watch;
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset ${s.bg} ${s.text} ${s.ring}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${s.dot}`} />
      {s.label}
      {typeof score === "number" && (
        <span className="opacity-75">· {Math.round(score)}</span>
      )}
    </span>
  );
}
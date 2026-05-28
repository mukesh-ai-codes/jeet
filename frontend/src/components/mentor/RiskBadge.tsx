"use client";

import type { RiskTier } from "@/types";

const STYLES: Record<RiskTier, { bg: string; text: string; ring: string; label: string }> = {
  urgent:   { bg: "bg-red-50",     text: "text-red-700",     ring: "ring-red-200",     label: "Urgent" },
  critical: { bg: "bg-orange-50",  text: "text-orange-700",  ring: "ring-orange-200",  label: "Critical" },
  watch:    { bg: "bg-amber-50",   text: "text-amber-700",   ring: "ring-amber-200",   label: "Watch" },
  stable:   { bg: "bg-emerald-50", text: "text-emerald-700", ring: "ring-emerald-200", label: "Stable" },
  lost:     { bg: "bg-slate-100",  text: "text-slate-600",   ring: "ring-slate-300",   label: "Lost" },
};

export default function RiskBadge({ tier, score }: { tier: RiskTier; score?: number }) {
  const s = STYLES[tier] || STYLES.watch;
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset ${s.bg} ${s.text} ${s.ring}`}>
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {s.label}
      {typeof score === "number" && (
        <span className="opacity-60">· {Math.round(score)}</span>
      )}
    </span>
  );
}

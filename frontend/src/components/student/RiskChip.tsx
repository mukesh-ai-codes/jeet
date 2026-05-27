"use client";

/**
 * RiskChip — displays a colored pill for a student's risk tier.
 *
 * Tiers map to your simulator's classification:
 *   stable    — green, "On track"
 *   watch     — amber, "Worth watching"
 *   critical  — orange, "Needs attention"
 *   urgent    — red, "Urgent: intervene"
 *   lost      — gray, "Already churned"
 */

import { Activity } from "lucide-react";

const RISK_STYLES: Record<string, { bg: string; text: string; ring: string; label: string }> = {
  stable: {
    bg: "bg-emerald-50",
    text: "text-emerald-700",
    ring: "ring-emerald-200",
    label: "On track",
  },
  watch: {
    bg: "bg-amber-50",
    text: "text-amber-700",
    ring: "ring-amber-200",
    label: "Worth watching",
  },
  critical: {
    bg: "bg-orange-50",
    text: "text-orange-700",
    ring: "ring-orange-200",
    label: "Needs attention",
  },
  urgent: {
    bg: "bg-red-50",
    text: "text-red-700",
    ring: "ring-red-200",
    label: "Urgent",
  },
  lost: {
    bg: "bg-slate-100",
    text: "text-slate-600",
    ring: "ring-slate-300",
    label: "Inactive",
  },
};

export default function RiskChip({ tier }: { tier: string | null | undefined }) {
  // Derive the style; default to stable if backend gives us anything weird
  const key = tier && RISK_STYLES[tier] ? tier : "stable";
  const s = RISK_STYLES[key];

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset ${s.bg} ${s.text} ${s.ring}`}
    >
      <Activity className="h-3 w-3" />
      {s.label}
    </span>
  );
}

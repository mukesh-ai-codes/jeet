"use client";

/**
 * StepInPanel — "When to step in" actionable guidance.
 *
 * Decision 2 = Option C: silent when nothing's wrong, specific when it is.
 *
 * Severity handling:
 *   urgent  → red panel, "Worth a conversation today"
 *   watch   → amber panel, gentle heads-up
 *   positive/info → NOT shown here (positives surface elsewhere as reassurance)
 *
 * If there are no urgent/watch insights, the whole panel renders as a calm
 * reassurance strip rather than disappearing entirely — so the parent knows
 * the absence is intentional ("nothing needs your attention"), not a bug.
 */

import { AlertTriangle, Info, Sparkles } from "lucide-react";
import type { WhisperInsight } from "@/types";

const SEVERITY_META: Record<string, { panel: string; icon: typeof AlertTriangle; iconColor: string; heading: string }> = {
  urgent: {
    panel: "border-red-200 bg-red-50",
    icon: AlertTriangle,
    iconColor: "text-red-600",
    heading: "Worth a conversation today",
  },
  watch: {
    panel: "border-amber-200 bg-amber-50",
    icon: Info,
    iconColor: "text-amber-600",
    heading: "A gentle heads-up",
  },
};

export default function StepInPanel({
  insights,
  childFirstName,
}: {
  insights: WhisperInsight[];
  childFirstName: string;
}) {
  const actionable = insights.filter(
    (i) => i.severity === "urgent" || i.severity === "watch"
  );
  const positives = insights.filter((i) => i.severity === "positive");

  // Calm state — nothing actionable
  if (actionable.length === 0) {
    return (
      <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-6">
        <div className="flex items-start gap-3">
          <Sparkles className="h-5 w-5 text-emerald-600 shrink-0 mt-0.5" />
          <div>
            <h3 className="font-display text-base font-semibold text-emerald-900">
              Nothing needs your attention right now
            </h3>
            <p className="mt-1 text-sm text-emerald-800 leading-relaxed">
              {childFirstName} is doing fine. JEET watches the signals daily
              and will tell you the moment a nudge from you would help — so you
              can relax until then.
            </p>
            {positives.length > 0 && (
              <ul className="mt-3 space-y-1.5">
                {positives.map((p, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-emerald-800">
                    <span className="mt-1 h-1.5 w-1.5 rounded-full bg-emerald-500 shrink-0" />
                    {p.message}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Actionable state
  return (
    <div className="space-y-3">
      <h3 className="font-display text-base font-semibold text-slate-900">
        When to step in
      </h3>
      {actionable.map((insight, i) => {
        const meta = SEVERITY_META[insight.severity] || SEVERITY_META.watch;
        const Icon = meta.icon;
        return (
          <div
            key={i}
            className={`rounded-2xl border p-5 ${meta.panel}`}
          >
            <div className="flex items-start gap-3">
              <Icon className={`h-5 w-5 shrink-0 mt-0.5 ${meta.iconColor}`} />
              <div>
                <p className="text-sm font-semibold text-slate-900">
                  {meta.heading}
                </p>
                <p className="mt-1 text-sm text-slate-700 leading-relaxed">
                  {insight.message}
                </p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

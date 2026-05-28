"use client";

/**
 * PositiveHighlights — surfaces what's going WELL for the child.
 *
 * Encouragement-first principle: even when a child is at risk, a parent
 * should see their wins. Pulls 'positive' severity insights from the
 * backend. Renders nothing if there are none (no fake positivity).
 */

import { Sparkles } from "lucide-react";
import type { WhisperInsight } from "@/types";

export default function PositiveHighlights({
  insights,
}: {
  insights: WhisperInsight[];
}) {
  const positives = insights.filter((i) => i.severity === "positive");

  if (positives.length === 0) return null;

  return (
    <div className="rounded-2xl border border-emerald-200 bg-gradient-to-br from-emerald-50 to-white p-5">
      <div className="flex items-center gap-2">
        <Sparkles className="h-4 w-4 text-emerald-600" />
        <h3 className="font-display text-sm font-semibold text-emerald-900">
          What&apos;s going well
        </h3>
      </div>
      <ul className="mt-3 space-y-2">
        {positives.map((p, i) => (
          <li
            key={i}
            className="flex items-start gap-2 text-sm text-emerald-800"
          >
            <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-emerald-500 shrink-0" />
            {p.message}
          </li>
        ))}
      </ul>
    </div>
  );
}

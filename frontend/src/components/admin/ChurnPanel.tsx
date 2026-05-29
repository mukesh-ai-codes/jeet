"use client";

/** Why students leave. The headline insight: silent disengagement + confidence
 *  collapse are exactly what JEET predicts — so most churn is preventable. */

import type { ChurnData } from "@/hooks/useAdminOverview";

const BAR_TONE: Record<string, string> = {
  engagement: "bg-orange-500",
  academic: "bg-red-500",
  attendance: "bg-amber-500",
  financial: "bg-rose-500",
  other: "bg-slate-300",
};

function toneFor(reason: string): string {
  const r = reason.toLowerCase();
  if (r.includes("engagement")) return BAR_TONE.engagement;
  if (r.includes("academic")) return BAR_TONE.academic;
  if (r.includes("attendance")) return BAR_TONE.attendance;
  if (r.includes("financial")) return BAR_TONE.financial;
  return BAR_TONE.other;
}

export default function ChurnPanel({ data }: { data: ChurnData | null }) {
  if (!data) return null;

  // Preventable = engagement + academic (what JEET's signals catch early)
  const preventable = data.breakdown
    .filter((b) => {
      const r = b.primary_reason.toLowerCase();
      return r.includes("engagement") || r.includes("academic");
    })
    .reduce((sum, b) => sum + b.percentage, 0);

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6">
      <div className="flex items-baseline justify-between">
        <h2 className="font-display text-xl font-bold text-slate-900">Why students leave</h2>
        <span className="text-sm text-slate-500">{data.total_churned.toLocaleString()} churned to date</span>
      </div>

      <div className="mt-3 rounded-xl bg-indigo-50 px-4 py-3 text-sm text-indigo-900">
        <span className="font-semibold">{preventable.toFixed(0)}% of churn is the kind JEET catches early</span>
        {" "}— silent disengagement and confidence collapse both show up in behavioral signals ~14 days before a student leaves.
      </div>

      <div className="mt-5 space-y-3">
        {data.breakdown.map((b) => (
          <div key={b.primary_reason}>
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-700">{b.primary_reason}</span>
              <span className="font-semibold text-slate-900">{b.percentage}%</span>
            </div>
            <div className="mt-1 h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
              <div
                className={`h-full rounded-full ${toneFor(b.primary_reason)}`}
                style={{ width: `${b.percentage}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

"use client";

/** Revenue by plan — captured vs failed. Money view for the buyer. */

import type { RevenueData } from "@/hooks/useAdminOverview";

function fmtL(inr: number) {
  if (inr >= 1e7) return `₹${(inr / 1e7).toFixed(2)} Cr`;
  return `₹${(inr / 1e5).toFixed(1)} L`;
}

export default function RevenuePanel({ data }: { data: RevenueData | null }) {
  if (!data) return null;
  const max = Math.max(...data.by_plan.map((p) => p.total_revenue_inr), 1);

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6">
      <div className="flex items-baseline justify-between">
        <h2 className="font-display text-xl font-bold text-slate-900">Revenue by plan</h2>
        <span className="text-sm text-slate-500">
          {fmtL(data.total_captured_inr)} captured · {fmtL(data.total_failed_attempts_inr)} failed
        </span>
      </div>

      <div className="mt-5 space-y-4">
        {data.by_plan.map((p) => (
          <div key={p.plan_slug}>
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium text-slate-700">{p.plan_name}</span>
              <span className="text-slate-500">
                {p.subscribers.toLocaleString()} subs · {fmtL(p.total_revenue_inr)}
              </span>
            </div>
            <div className="mt-1 h-3 w-full overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full bg-indigo-500"
                style={{ width: `${(p.total_revenue_inr / max) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

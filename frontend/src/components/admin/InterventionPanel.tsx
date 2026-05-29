"use client";

/** Are interventions working? Success rate + avg risk reduction by type.
 *  This is the ROI panel — proof the product changes outcomes. */

import type { InterventionData } from "@/hooks/useAdminOverview";

const LABELS: Record<string, string> = {
  mentor_message: "Mentor message",
  parent_email: "Parent email",
  mentor_call: "Mentor call",
  wellness_check: "Wellness check",
  tutor_session: "Tutor session",
  parent_call: "Parent call",
};

export default function InterventionPanel({ data }: { data: InterventionData | null }) {
  if (!data) return null;

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6">
      <div className="flex items-baseline justify-between">
        <h2 className="font-display text-xl font-bold text-slate-900">Are interventions working?</h2>
        <span className="text-sm text-slate-500">{data.total_interventions} logged</span>
      </div>

      <div className="mt-3 flex flex-wrap gap-6">
        <div>
          <div className="text-3xl font-bold text-emerald-700">{data.overall_success_rate}%</div>
          <div className="text-sm text-slate-500">overall success rate</div>
        </div>
      </div>

      <div className="mt-5 overflow-hidden rounded-xl border border-slate-100">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-2">Type</th>
              <th className="px-4 py-2 text-right">Logged</th>
              <th className="px-4 py-2 text-right">Success</th>
              <th className="px-4 py-2 text-right">Avg risk drop</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {data.by_type.map((t) => (
              <tr key={t.intervention_type}>
                <td className="px-4 py-2.5 text-slate-700">{LABELS[t.intervention_type] || t.intervention_type}</td>
                <td className="px-4 py-2.5 text-right text-slate-600">{t.total_count}</td>
                <td className="px-4 py-2.5 text-right font-semibold text-slate-900">{t.success_rate}%</td>
                <td className="px-4 py-2.5 text-right font-semibold text-emerald-700">−{t.avg_risk_reduction.toFixed(0)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

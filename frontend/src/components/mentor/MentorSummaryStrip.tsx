"use client";

/**
 * MentorSummaryStrip — compact top strip showing the day's triage state.
 *
 * Three numbers, one chip: total at-risk, urgent count, critical+watch count,
 * and a cohort label so the mentor knows they're looking at the right pod.
 */

import { AlertCircle, Users, Layers } from "lucide-react";
import type { AtRiskListResponse, MentorCohort } from "@/types";

export default function MentorSummaryStrip({
  queue,
  cohorts,
}: {
  queue: AtRiskListResponse | null;
  cohorts: MentorCohort[];
}) {
  const total = queue?.total_at_risk ?? 0;
  const urgent = queue?.urgent_count ?? 0;
  const critical = (queue?.critical_count ?? 0) + (queue?.watch_count ?? 0);
  const totalStudents = cohorts.reduce((sum, c) => sum + (c.active_students || 0), 0);

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      <StripTile
        label="Need attention today"
        value={String(total)}
        sub={`of ${totalStudents} active`}
        icon={AlertCircle}
        tone="text-slate-900"
      />
      <StripTile
        label="Urgent"
        value={String(urgent)}
        sub="risk_score ≥ 70"
        icon={AlertCircle}
        tone="text-red-700"
      />
      <StripTile
        label="Critical + Watch"
        value={String(critical)}
        sub="early warning"
        icon={AlertCircle}
        tone="text-amber-700"
      />
      <StripTile
        label="Cohorts"
        value={String(cohorts.length)}
        sub={`${totalStudents} active`}
        icon={Layers}
        tone="text-slate-900"
      />
    </div>
  );
}

function StripTile({
  label, value, sub, icon: Icon, tone,
}: {
  label: string; value: string; sub: string; icon: typeof AlertCircle; tone: string;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white px-4 py-3">
      <div className="flex items-center gap-1.5 text-[11px] text-slate-500 uppercase tracking-wide font-semibold">
        <Icon className="h-3 w-3" />
        {label}
      </div>
      <div className={`mt-1 font-display text-2xl font-bold ${tone}`}>{value}</div>
      <div className="text-[11px] text-slate-500 mt-0.5">{sub}</div>
    </div>
  );
}

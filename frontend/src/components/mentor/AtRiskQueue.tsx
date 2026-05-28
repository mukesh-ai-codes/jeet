"use client";

import type { AtRiskListResponse, AtRiskStudent } from "@/types";
import AtRiskRow from "./AtRiskRow";
import { Users } from "lucide-react";

export default function AtRiskQueue({
  queue,
  onOpen,
}: {
  queue: AtRiskListResponse | null;
  onOpen: (s: AtRiskStudent) => void;
}) {
  if (!queue || queue.students.length === 0) {
    return (
      <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-8 text-center">
        <Users className="h-8 w-8 text-emerald-600 mx-auto" />
        <h3 className="mt-3 font-display text-base font-semibold text-emerald-900">
          No students need attention right now
        </h3>
        <p className="mt-1 text-sm text-emerald-800">
          JEET is monitoring everyone in your cohorts. We&apos;ll surface anyone
          who slips here.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white overflow-hidden">
      <div className="px-5 py-3 border-b border-slate-100 bg-slate-50 flex items-center justify-between">
        <h2 className="font-display text-sm font-semibold text-slate-900">
          Today&apos;s triage queue
        </h2>
        <span className="text-xs text-slate-500">
          Ranked by risk score · {queue.students.length} students
        </span>
      </div>
      <div className="divide-y divide-slate-100">
        {queue.students.map((s) => (
          <AtRiskRow key={s.student_user_id} student={s} onOpen={onOpen} />
        ))}
      </div>
    </div>
  );
}

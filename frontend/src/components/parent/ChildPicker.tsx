"use client";

/**
 * ChildPicker — lets a parent switch between children.
 *
 * Single child  → shows a static header (no picker UI needed)
 * Multiple kids → shows pill tabs, one per child, active highlighted
 */

import type { ChildSummary } from "@/types";

const TARGET_EXAM_LABEL: Record<string, string> = {
  jee_main: "JEE Main",
  jee_advanced: "JEE Advanced",
  neet_ug: "NEET",
  foundation: "Foundation",
  board: "Boards",
};

function initials(name: string): string {
  return name
    .split(" ")
    .map((p) => p[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

export default function ChildPicker({
  children,
  selectedId,
  onSelect,
}: {
  children: ChildSummary[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}) {
  if (children.length === 0) return null;

  // Single child — clean static header
  if (children.length === 1) {
    const c = children[0];
    return (
      <div className="flex items-center gap-3">
        <div className="h-11 w-11 rounded-full bg-indigo-600 text-white text-sm font-bold flex items-center justify-center">
          {initials(c.full_name)}
        </div>
        <div>
          <p className="font-display text-lg font-bold text-slate-900 leading-tight">
            {c.full_name}
          </p>
          <p className="text-xs text-slate-500">
            Class {c.grade} ·{" "}
            {TARGET_EXAM_LABEL[c.target_exam] || c.target_exam} · {c.program_name}
          </p>
        </div>
      </div>
    );
  }

  // Multiple children — pill tabs
  return (
    <div>
      <p className="text-xs font-semibold text-slate-500 mb-2">
        Your children
      </p>
      <div className="flex flex-wrap gap-2">
        {children.map((c) => {
          const active = c.student_user_id === selectedId;
          return (
            <button
              key={c.student_user_id}
              type="button"
              onClick={() => onSelect(c.student_user_id)}
              className={`flex items-center gap-2 rounded-full border px-3 py-1.5 transition ${
                active
                  ? "border-indigo-500 bg-indigo-50 ring-2 ring-indigo-100"
                  : "border-slate-200 bg-white hover:border-slate-300"
              }`}
            >
              <span
                className={`h-6 w-6 rounded-full text-[10px] font-bold flex items-center justify-center ${
                  active ? "bg-indigo-600 text-white" : "bg-slate-200 text-slate-700"
                }`}
              >
                {initials(c.full_name)}
              </span>
              <span
                className={`text-sm ${
                  active ? "font-semibold text-slate-900" : "text-slate-700"
                }`}
              >
                {c.full_name.split(" ")[0]}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

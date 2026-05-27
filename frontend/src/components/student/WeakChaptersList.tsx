"use client";

/**
 * WeakChaptersList — focused list of chapters where the student is dipping.
 *
 * Data: weakChapters.weak_chapters (array of WeakChapter)
 *
 * Each item: chapter name, subject, avg score percentage, attempts count.
 */

import { TrendingDown } from "lucide-react";
import type { WeakChapter } from "@/types";

function scoreColor(pct: number): string {
  if (pct >= 55) return "text-amber-700 bg-amber-50";
  return "text-red-700 bg-red-50";
}

export default function WeakChaptersList({
  chapters,
}: {
  chapters: WeakChapter[];
}) {
  if (!chapters || chapters.length === 0) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-6">
        <h3 className="font-display text-base font-semibold text-slate-900">
          Weak chapters
        </h3>
        <div className="mt-6 text-center py-8">
          <TrendingDown className="h-8 w-8 text-emerald-300 mx-auto" />
          <p className="mt-3 text-sm text-slate-500">
            No weak chapters yet. Keep it up!
          </p>
        </div>
      </div>
    );
  }

  const top = chapters.slice(0, 5);

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6">
      <div className="flex items-end justify-between mb-4">
        <div>
          <h3 className="font-display text-base font-semibold text-slate-900">
            Weak chapters
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Where you're losing the most marks
          </p>
        </div>
        <span className="text-xs text-slate-500">
          Top {top.length} of {chapters.length}
        </span>
      </div>

      <div className="space-y-2.5">
        {top.map((c, i) => {
          const pct = Math.round(c.avg_score);
          return (
            <div
              key={i}
              className="flex items-center justify-between gap-3 rounded-lg border border-slate-100 bg-slate-50 px-3 py-2.5"
            >
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-slate-900 truncate">
                  {c.chapter}
                </p>
                <p className="text-xs text-slate-500 mt-0.5">
                  {c.subject_name} · {c.quizzes_attempted}{" "}
                  attempt{c.quizzes_attempted === 1 ? "" : "s"}
                </p>
              </div>
              <span
                className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-semibold ${scoreColor(pct)}`}
              >
                {pct}%
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

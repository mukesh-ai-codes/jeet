"use client";

/**
 * PlaceholderPanel — visual placeholder for Days 13–15 dashboards.
 *
 * Communicates:
 *   - "You're logged in as X, in the right place"
 *   - What's coming on this surface
 *   - A clear note that it's a Day 12 milestone, not a broken page
 *
 * Will be deleted as each dashboard's real version ships.
 */

import { LucideIcon } from "lucide-react";

type Module = {
  icon: LucideIcon;
  name: string;
  description: string;
};

type Props = {
  badge: string;
  title: string;
  subtitle: string;
  modules: Module[];
  shipsOn: string; // e.g. "Day 13"
};

export default function PlaceholderPanel({
  badge,
  title,
  subtitle,
  modules,
  shipsOn,
}: Props) {
  return (
    <div>
      {/* Hero */}
      <div className="inline-flex items-center gap-2 rounded-full border border-indigo-200 bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700">
        <span className="h-1.5 w-1.5 rounded-full bg-orange-500 animate-pulse" />
        {badge}
      </div>

      <h1 className="mt-4 font-display text-3xl md:text-4xl font-bold text-slate-900 leading-tight">
        {title}
      </h1>
      <p className="mt-3 text-slate-600 max-w-2xl">{subtitle}</p>

      {/* Module cards — visual placeholders */}
      <div className="mt-10 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {modules.map((m) => {
          const Icon = m.icon;
          return (
            <div
              key={m.name}
              className="rounded-xl border border-dashed border-slate-300 bg-white p-5"
            >
              <div className="rounded-lg bg-indigo-50 p-2 inline-flex">
                <Icon className="h-5 w-5 text-indigo-600" />
              </div>
              <h3 className="mt-4 text-base font-semibold text-slate-900">
                {m.name}
              </h3>
              <p className="mt-1 text-sm text-slate-600 leading-relaxed">
                {m.description}
              </p>
              <div className="mt-4 inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500">
                <span className="h-1.5 w-1.5 rounded-full bg-slate-400" />
                Ships {shipsOn}
              </div>
            </div>
          );
        })}
      </div>

      {/* Status footer */}
      <div className="mt-12 rounded-xl border border-slate-200 bg-white px-5 py-4 flex items-start gap-3">
        <div className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-semibold text-emerald-700">
          Day 12 · Done
        </div>
        <p className="text-sm text-slate-600">
          Auth flow + role-based routing + admin onboarding are live. The
          dashboard you see fills in across {shipsOn} and the days right after.
        </p>
      </div>
    </div>
  );
}

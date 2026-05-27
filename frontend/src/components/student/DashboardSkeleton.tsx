"use client";

/**
 * DashboardSkeleton — shimmer placeholder rendered while the dashboard loads.
 *
 * Mirrors the real layout (welcome row + 3 plan cards + Tara block + sections),
 * so the page doesn't "jump" when real content arrives.
 */

function Shimmer({ className = "" }: { className?: string }) {
  return (
    <div
      className={`animate-pulse bg-gradient-to-r from-slate-200 via-slate-100 to-slate-200 bg-[length:200%_100%] rounded ${className}`}
    />
  );
}

function PlanCardSkeleton() {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5">
      <div className="flex items-start justify-between">
        <Shimmer className="h-9 w-9 rounded-lg" />
        <Shimmer className="h-3 w-12" />
      </div>
      <Shimmer className="mt-4 h-3 w-24" />
      <Shimmer className="mt-2 h-5 w-full" />
      <Shimmer className="mt-1.5 h-3 w-3/4" />
      <Shimmer className="mt-3 h-3 w-full" />
      <Shimmer className="mt-1.5 h-3 w-5/6" />
      <div className="mt-4 flex items-center justify-between">
        <Shimmer className="h-3 w-24" />
        <Shimmer className="h-3 w-12" />
      </div>
    </div>
  );
}

function SectionSkeleton({ tall = false }: { tall?: boolean }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6">
      <Shimmer className="h-4 w-40" />
      <Shimmer className="mt-2 h-3 w-56" />
      <div className="mt-6 space-y-3">
        <Shimmer className="h-4 w-full" />
        <Shimmer className="h-4 w-11/12" />
        <Shimmer className="h-4 w-10/12" />
        {tall && (
          <>
            <Shimmer className="h-4 w-11/12" />
            <Shimmer className="h-4 w-9/12" />
          </>
        )}
      </div>
    </div>
  );
}

export default function DashboardSkeleton() {
  return (
    <div className="space-y-10">
      {/* Welcome row */}
      <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
        <div className="flex-1">
          <Shimmer className="h-3 w-44" />
          <Shimmer className="mt-3 h-8 w-72" />
          <Shimmer className="mt-2 h-3 w-56" />
        </div>
        <div className="flex items-center gap-3">
          <Shimmer className="h-7 w-28 rounded-full" />
          <Shimmer className="h-7 w-28 rounded-full" />
        </div>
      </div>

      {/* Plan cards */}
      <div>
        <Shimmer className="h-5 w-32" />
        <Shimmer className="mt-2 h-3 w-80" />
        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          <PlanCardSkeleton />
          <PlanCardSkeleton />
          <PlanCardSkeleton />
        </div>
      </div>

      {/* Tara teaser placeholder */}
      <div className="rounded-2xl bg-gradient-to-br from-indigo-100 via-indigo-50 to-white p-8">
        <Shimmer className="h-6 w-64" />
        <Shimmer className="mt-3 h-3 w-full max-w-xl" />
        <Shimmer className="mt-2 h-3 w-2/3 max-w-md" />
      </div>

      {/* Section row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <SectionSkeleton tall />
        </div>
        <SectionSkeleton />
      </div>

      {/* Section row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SectionSkeleton tall />
        <SectionSkeleton tall />
      </div>
    </div>
  );
}

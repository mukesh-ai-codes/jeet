"use client";

import { TrendingUp, Users, Wallet, CheckCircle2 } from "lucide-react";

import ProtectedRoute from "@/components/auth/ProtectedRoute";
import AppShell from "@/components/app/AppShell";
import { useAdminOverview } from "@/hooks/useAdminOverview";
import ChurnPanel from "@/components/admin/ChurnPanel";
import InterventionPanel from "@/components/admin/InterventionPanel";
import RevenuePanel from "@/components/admin/RevenuePanel";

function fmtCr(inr: number) {
  return `₹${(inr / 1e7).toFixed(2)} Cr`;
}

function KpiTile({
  label, value, sub, icon: Icon, tone = "text-slate-900",
}: {
  label: string; value: string; sub?: string;
  icon: React.ComponentType<{ className?: string }>; tone?: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5">
      <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
        <Icon className="h-4 w-4" />
        {label}
      </div>
      <div className={`mt-2 text-3xl font-bold ${tone}`}>{value}</div>
      {sub && <div className="mt-1 text-sm text-slate-500">{sub}</div>}
    </div>
  );
}

export default function AdminDashboardPage() {
  const { overview, revenue, churn, interventions, loading } = useAdminOverview();

  return (
    <ProtectedRoute allowedRoles={["admin"]}>
      <AppShell>
        <div className="space-y-10">
          <header>
            <p className="text-sm font-semibold text-indigo-600">Command Center</p>
            <h1 className="font-display text-3xl font-bold text-slate-900">
              Your institute, at a glance.
            </h1>
            <p className="mt-1 text-slate-600">
              Retention health, why students leave, and whether your mentors&apos;
              interventions are working.
            </p>
          </header>

          {loading ? (
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              {[0, 1, 2, 3].map((i) => (
                <div key={i} className="h-28 animate-pulse rounded-2xl bg-slate-100" />
              ))}
            </div>
          ) : (
            <>
              {/* Top KPI row */}
              <section className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <KpiTile
                  label="Retention"
                  value={overview ? `${overview.retention_pct}%` : "—"}
                  sub={overview ? `${overview.active_subscriptions.toLocaleString()} active students` : undefined}
                  icon={TrendingUp}
                  tone="text-emerald-700"
                />
                <KpiTile
                  label="At-risk of churn"
                  value={overview ? overview.churned_subscriptions.toLocaleString() : "—"}
                  sub="students lost to date"
                  icon={Users}
                  tone="text-red-700"
                />
                <KpiTile
                  label="Revenue captured"
                  value={overview ? fmtCr(overview.total_revenue_inr) : "—"}
                  sub="lifetime, across all plans"
                  icon={Wallet}
                />
                <KpiTile
                  label="Payment success"
                  value={overview ? `${(overview.payment_success_rate * 100).toFixed(1)}%` : "—"}
                  sub="captured vs attempted"
                  icon={CheckCircle2}
                />
              </section>

              <ChurnPanel data={churn} />
              <InterventionPanel data={interventions} />
              <RevenuePanel data={revenue} />
            </>
          )}
        </div>
      </AppShell>
    </ProtectedRoute>
  );
}

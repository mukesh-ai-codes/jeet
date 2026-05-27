"use client";

/**
 * /onboarding/admin — wizard the first time an admin signs into JEET.
 *
 * Guarded by ProtectedRoute with allowDuringOnboarding so the redirect
 * loop doesn't fire on this page itself.
 */

import Link from "next/link";
import Logo from "@/components/shared/Logo";
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import AdminWizard from "@/components/onboarding/AdminWizard";

export default function AdminOnboardingPage() {
  return (
    <ProtectedRoute allowedRoles={["admin"]} allowDuringOnboarding>
      <div className="min-h-screen bg-slate-50">
        <header className="border-b border-slate-200 bg-white">
          <div className="mx-auto max-w-3xl px-6 py-4 flex items-center justify-between">
            <Link href="/" className="inline-flex">
              <Logo size="sm" />
            </Link>
            <span className="text-xs text-slate-500">
              Workspace setup · ~2 min
            </span>
          </div>
        </header>

        <div className="mx-auto max-w-3xl px-6 py-10">
          <div className="inline-flex items-center gap-2 rounded-full border border-indigo-200 bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700">
            <span className="h-1.5 w-1.5 rounded-full bg-orange-500 animate-pulse" />
            Step 1 of 1 · Tell us about your institute
          </div>

          <h1 className="mt-4 font-display text-3xl md:text-4xl font-bold text-slate-900 leading-tight">
            Let&apos;s set up your retention OS.
          </h1>
          <p className="mt-3 text-slate-600 max-w-2xl">
            Eight quick questions. We&apos;ll use these to tailor your trial
            cohort, recommend the right modules to start with, and build a
            custom retention baseline for your institute.
          </p>
        </div>

        <main className="mx-auto max-w-3xl px-6 pb-16">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 md:p-12 shadow-sm">
            <AdminWizard />
          </div>

          <p className="mt-6 text-center text-xs text-slate-500">
            Need to step away? Your progress isn&apos;t saved yet — but the
            form is fast. Finish in one sitting.
          </p>
        </main>
      </div>
    </ProtectedRoute>
  );
}

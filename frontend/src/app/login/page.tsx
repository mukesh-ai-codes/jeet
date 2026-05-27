"use client";

/**
 * /login — entry route for unauthenticated users.
 *
 * Layout: split-screen on desktop (form left, brand panel right),
 * single column on mobile. The brand panel is decorative — pulls
 * visual continuity from the marketing hero (Signal Waves motif).
 */

import { useEffect, Suspense } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

import Logo from "@/components/shared/Logo";
import LoginForm from "@/components/auth/LoginForm";
import { useAuth } from "@/hooks/useAuth";
import { landingPathFor } from "@/lib/routes";

function BrandPanel() {
  return (
    <div className="hidden lg:flex relative bg-gradient-to-br from-indigo-600 via-indigo-700 to-indigo-900 text-white overflow-hidden">
      {/* Decorative concentric arcs — echoes the Signal Waves logo */}
      <svg
        viewBox="0 0 600 600"
        className="absolute inset-0 w-full h-full opacity-30"
        preserveAspectRatio="xMidYMid slice"
      >
        <defs>
          <radialGradient id="loginGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#F97316" stopOpacity="0.4" />
            <stop offset="100%" stopColor="#F97316" stopOpacity="0" />
          </radialGradient>
        </defs>
        <circle cx="300" cy="300" r="250" fill="url(#loginGlow)" />
        <circle cx="300" cy="300" r="220" fill="none" stroke="white" strokeWidth="1.5" strokeOpacity="0.2" />
        <circle cx="300" cy="300" r="170" fill="none" stroke="white" strokeWidth="1.5" strokeOpacity="0.35" />
        <circle cx="300" cy="300" r="120" fill="none" stroke="white" strokeWidth="2" strokeOpacity="0.6" />
        <circle cx="300" cy="300" r="22" fill="#F97316" />
      </svg>

      <div className="relative z-10 flex flex-col justify-between p-12 w-full">
        <Link href="/" className="inline-flex">
          <Logo size="md" variant="white" />
        </Link>

        <div className="max-w-md">
          <p className="text-xs font-semibold uppercase tracking-widest text-indigo-200">
            Retention OS
          </p>
          <h2 className="mt-3 font-display text-3xl font-bold leading-tight">
            Catch dropouts before they happen.
          </h2>
          <p className="mt-4 text-indigo-100 text-sm leading-relaxed">
            JEET surfaces at-risk students 14 days early and gives your
            mentors the exact playbook to save them.
          </p>

          <div className="mt-8 grid grid-cols-3 gap-4">
            <div>
              <div className="text-2xl font-bold">14d</div>
              <div className="text-xs text-indigo-200 mt-1">Early warning</div>
            </div>
            <div>
              <div className="text-2xl font-bold">+12%</div>
              <div className="text-xs text-indigo-200 mt-1">Retention lift</div>
            </div>
            <div>
              <div className="text-2xl font-bold">₹10L+</div>
              <div className="text-xs text-indigo-200 mt-1">LTV saved</div>
            </div>
          </div>
        </div>

        <p className="text-xs text-indigo-300">
          © 2026 JEET · Stop dropouts before they start.
        </p>
      </div>
    </div>
  );
}

function LoginContent() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading } = useAuth();

  // If a logged-in user lands on /login (e.g. via bookmark), bounce them
  // to their landing page. We do this after auth has settled.
  useEffect(() => {
    if (isLoading) return;
    if (isAuthenticated && user) {
      router.replace(landingPathFor(user));
    }
  }, [isLoading, isAuthenticated, user, router]);

  return (
    <div className="min-h-screen grid grid-cols-1 lg:grid-cols-2 bg-white">
      {/* LEFT — Form */}
      <div className="flex flex-col">
        {/* Mobile-only top bar with logo */}
        <div className="lg:hidden border-b border-slate-200 px-6 py-4">
          <Link href="/" className="inline-flex">
            <Logo size="sm" />
          </Link>
        </div>

        <div className="flex-1 flex items-center justify-center px-6 py-12">
          <div className="w-full max-w-sm">
            <div className="mb-8">
              <h1 className="font-display text-3xl font-bold text-slate-900">
                Welcome back
              </h1>
              <p className="mt-2 text-sm text-slate-600">
                Sign in to your JEET workspace
              </p>
            </div>

            <LoginForm />

            <p className="mt-8 text-xs text-center text-slate-500">
              New institute?{" "}
              <Link
                href="/"
                className="text-indigo-600 hover:text-indigo-700 font-medium"
              >
                Book a demo
              </Link>{" "}
              to get started.
            </p>
          </div>
        </div>
      </div>

      {/* RIGHT — Brand panel (desktop only) */}
      <BrandPanel />
    </div>
  );
}

export default function LoginPage() {
  // Suspense wrapper is required because useSearchParams() inside LoginForm
  // suspends during the static render Next.js does at build time.
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-white">
          <div className="h-8 w-8 rounded-full border-2 border-indigo-200 border-t-indigo-600 animate-spin" />
        </div>
      }
    >
      <LoginContent />
    </Suspense>
  );
}

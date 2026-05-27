"use client";

/**
 * AppShell — shared chrome for authenticated pages.
 *
 * Provides:
 *   - Top bar with logo (links to landing), workspace label, user menu
 *   - Logout button
 *   - Main content area with a max-width container
 *
 * Days 13–15 will likely extract a sidebar for the admin / mentor views
 * once those have multiple sub-routes. For Day 12 placeholders, one shell
 * is enough.
 */

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { LogOut, ChevronDown, Sparkles } from "lucide-react";

import Logo from "@/components/shared/Logo";
import { useAuth } from "@/hooks/useAuth";

const ROLE_LABEL: Record<string, string> = {
  admin: "Institute Admin",
  mentor: "Mentor",
  student: "Student",
  parent: "Parent",
};

export default function AppShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  if (!user) return null;

  function handleLogout() {
    logout();
    router.replace("/login");
  }

  const initials =
    user.full_name
      ?.split(" ")
      .map((p) => p[0])
      .slice(0, 2)
      .join("")
      .toUpperCase() || "?";

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl px-6 py-3 flex items-center justify-between gap-4">
          <Link href="/" className="inline-flex shrink-0">
            <Logo size="sm" />
          </Link>

          <div className="hidden md:flex items-center gap-2 text-xs text-slate-500">
            <Sparkles className="h-3.5 w-3.5 text-indigo-500" />
            <span className="font-medium text-slate-700">Demo Coaching Institute</span>
            <span className="text-slate-300">·</span>
            <span>{ROLE_LABEL[user.role] || user.role}</span>
          </div>

          {/* User menu */}
          <div className="relative">
            <button
              type="button"
              onClick={() => setMenuOpen((o) => !o)}
              className="flex items-center gap-2 rounded-full border border-slate-200 bg-white pl-1.5 pr-2.5 py-1.5 hover:border-slate-300 transition"
            >
              <span className="h-7 w-7 rounded-full bg-indigo-600 text-white text-xs font-bold flex items-center justify-center">
                {initials}
              </span>
              <span className="hidden sm:inline text-sm text-slate-700">
                {user.full_name?.split(" ")[0]}
              </span>
              <ChevronDown className="h-3.5 w-3.5 text-slate-500" />
            </button>

            {menuOpen && (
              <>
                {/* Backdrop to close on outside click */}
                <div
                  className="fixed inset-0 z-10"
                  onClick={() => setMenuOpen(false)}
                />
                <div className="absolute right-0 mt-2 w-60 rounded-lg border border-slate-200 bg-white shadow-lg z-20 overflow-hidden">
                  <div className="px-4 py-3 border-b border-slate-100">
                    <div className="text-sm font-semibold text-slate-900 truncate">
                      {user.full_name}
                    </div>
                    <div className="text-xs text-slate-500 truncate">{user.email}</div>
                  </div>
                  <button
                    type="button"
                    onClick={handleLogout}
                    className="flex w-full items-center gap-2 px-4 py-2.5 text-sm text-slate-700 hover:bg-slate-50"
                  >
                    <LogOut className="h-4 w-4" />
                    Sign out
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-10">{children}</main>
    </div>
  );
}

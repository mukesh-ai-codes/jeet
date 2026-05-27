"use client";

/**
 * /student/lesson/[id] — lesson detail page.
 *
 * Day 13 scope (intentional, see Phase 4 strategic notes):
 *   - Shows lesson metadata (subject, chapter, duration, difficulty)
 *   - Shows description
 *   - Notes / video URLs displayed as disabled CTAs ("Coming soon —
 *     content sync") since the seeded CDN URLs don't actually resolve.
 *     Real institutes will replace these with their own CDN.
 *   - "Mark as started" button writes an event (Phase 5)
 *   - "Ask Tara" cross-promo card teasing the AI tutor
 *   - Related lessons sidebar (same chapter)
 *   - "Next lesson in chapter" CTA at the bottom
 */

import { use, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ArrowLeft,
  ArrowRight,
  Clock,
  Layers,
  PlayCircle,
  FileText,
  Sparkles,
  Loader2,
  AlertCircle,
  BookOpen,
} from "lucide-react";

import ProtectedRoute from "@/components/auth/ProtectedRoute";
import AppShell from "@/components/app/AppShell";
import MarkAsStartedButton from "@/components/student/MarkAsStartedButton";
import { courseApi, getErrorMessage } from "@/lib/api";
import type { LessonDetail, LessonSummary } from "@/types";

const DIFFICULTY_LABEL: Record<number, string> = {
  1: "Easy",
  2: "Easy",
  3: "Moderate",
  4: "Hard",
  5: "Hard",
};

export default function LessonDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  return (
    <ProtectedRoute allowedRoles={["student"]}>
      <AppShell>
        <LessonDetailContent params={params} />
      </AppShell>
    </ProtectedRoute>
  );
}

function LessonDetailContent({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  // In Next.js 16, params is a Promise; use() unwraps it inside a client component.
  const { id } = use(params);
  const router = useRouter();

  const [lesson, setLesson] = useState<LessonDetail | null>(null);
  const [related, setRelated] = useState<LessonSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const lessonData = await courseApi.getLesson(id);
        if (cancelled) return;
        setLesson(lessonData);

        // Fetch related lessons in the same chapter
        try {
          const list = await courseApi.listLessonsByChapter(lessonData.chapter);
          if (cancelled) return;
          // Exclude the current lesson, keep ordering, max 6
          setRelated(
            list.lessons.filter((l) => l.id !== id).slice(0, 6)
          );
        } catch {
          // Related lessons are nice-to-have; ignore failure
          if (!cancelled) setRelated([]);
        }
      } catch (err) {
        if (!cancelled) setError(getErrorMessage(err));
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="h-7 w-7 animate-spin text-indigo-600" />
          <p className="text-sm text-slate-500">Loading lesson…</p>
        </div>
      </div>
    );
  }

  if (error || !lesson) {
    return (
      <div className="max-w-md mx-auto mt-16 rounded-2xl border border-red-200 bg-red-50 p-6 text-center">
        <AlertCircle className="h-8 w-8 text-red-500 mx-auto" />
        <h2 className="mt-4 font-display text-lg font-bold text-slate-900">
          Couldn't load this lesson
        </h2>
        <p className="mt-2 text-sm text-slate-600">
          {error || "Lesson not found."}
        </p>
        <button
          type="button"
          onClick={() => router.push("/student")}
          className="mt-5 inline-flex items-center gap-1.5 rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white hover:bg-indigo-700"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to dashboard
        </button>
      </div>
    );
  }

  // Find the next lesson in the chapter (by sequence_order)
  const nextLesson = related.find(
    (l) => l.sequence_order > lesson.sequence_order
  );

  return (
    <div className="space-y-8">
      {/* Back link */}
      <Link
        href="/student"
        className="inline-flex items-center gap-1.5 text-sm text-slate-600 hover:text-slate-900"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to dashboard
      </Link>

      {/* Lesson header */}
      <header>
        <p className="text-xs font-semibold uppercase tracking-widest text-indigo-600">
          {lesson.subject_name} · {lesson.chapter}
        </p>
        <h1 className="mt-2 font-display text-3xl md:text-4xl font-bold text-slate-900 leading-tight">
          {lesson.title}
        </h1>

        <div className="mt-4 flex flex-wrap items-center gap-2">
          <Pill icon={Clock} text={`${lesson.duration_minutes} min`} />
          <Pill
            icon={Layers}
            text={DIFFICULTY_LABEL[lesson.difficulty_level] || "Moderate"}
          />
          <Pill icon={BookOpen} text={`Lesson #${lesson.sequence_order}`} />
        </div>
      </header>

      {/* Body grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* LEFT — Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Content placeholder card (no real video on Day 13) */}
          <div className="rounded-2xl border border-slate-200 bg-white overflow-hidden">
            <div className="aspect-video bg-gradient-to-br from-slate-100 via-slate-50 to-white flex items-center justify-center border-b border-slate-200">
              <div className="text-center px-6">
                <PlayCircle className="h-12 w-12 text-slate-300 mx-auto" />
                <p className="mt-4 text-sm font-semibold text-slate-700">
                  Lesson content
                </p>
                <p className="mt-1 text-xs text-slate-500 max-w-md">
                  Your institute will sync video and notes here. Until then,
                  use this lesson as a marker — JEET tracks your start time
                  to feed your engagement signals.
                </p>
              </div>
            </div>

            {lesson.description && (
              <div className="p-5">
                <p className="text-xs font-semibold uppercase tracking-widest text-slate-500">
                  About this lesson
                </p>
                <p className="mt-2 text-sm text-slate-700 leading-relaxed">
                  {lesson.description}
                </p>
              </div>
            )}

            {/* Primary CTA */}
            <div className="border-t border-slate-100 p-5">
              <MarkAsStartedButton lessonId={lesson.id} chapterName={lesson.chapter} />
            </div>
          </div>

          {/* Ask Tara teaser */}
          <div className="rounded-2xl border border-indigo-200 bg-gradient-to-br from-indigo-50 to-white p-5">
            <div className="flex items-start gap-3">
              <div className="rounded-lg bg-indigo-600 p-2 shrink-0">
                <Sparkles className="h-4 w-4 text-white" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-slate-900">
                  Stuck on this concept? Ask Tara.
                </h3>
                <p className="mt-1 text-sm text-slate-600 leading-relaxed">
                  Once Tara launches (Day 20), you'll be able to ask any
                  doubt about <span className="font-medium">{lesson.chapter}</span>{" "}
                  and get a RAG-grounded explanation with Indian-context
                  analogies — built for the JEE/NEET student, not generic ChatGPT.
                </p>
                <div className="mt-3 inline-flex items-center gap-1.5 rounded-full bg-white px-2.5 py-1 text-xs font-semibold text-indigo-700 ring-1 ring-inset ring-indigo-200">
                  <span className="h-1.5 w-1.5 rounded-full bg-orange-500 animate-pulse" />
                  Launching next week
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT — Sidebar */}
        <aside className="space-y-6">
          {/* Resources card */}
          <div className="rounded-2xl border border-slate-200 bg-white p-5">
            <h3 className="font-display text-base font-semibold text-slate-900">
              Lesson resources
            </h3>

            <div className="mt-4 space-y-2">
              <ResourceLink
                icon={PlayCircle}
                label="Video lecture"
                hint="Synced from institute CDN"
                available={false}
              />
              <ResourceLink
                icon={FileText}
                label="Notes PDF"
                hint="Synced from institute CDN"
                available={false}
              />
            </div>
          </div>

          {/* Related lessons */}
          {related.length > 0 && (
            <div className="rounded-2xl border border-slate-200 bg-white p-5">
              <h3 className="font-display text-base font-semibold text-slate-900">
                More in this chapter
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                {lesson.chapter}
              </p>

              <div className="mt-4 space-y-1.5">
                {related.map((l) => (
                  <Link
                    key={l.id}
                    href={`/student/lesson/${l.id}`}
                    className="block rounded-lg border border-slate-100 bg-slate-50 px-3 py-2.5 hover:bg-indigo-50 hover:border-indigo-200 transition"
                  >
                    <p className="text-sm font-medium text-slate-900 line-clamp-1">
                      {l.title}
                    </p>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Lesson #{l.sequence_order} · {l.duration_minutes} min ·{" "}
                      {DIFFICULTY_LABEL[l.difficulty_level] || "Moderate"}
                    </p>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </aside>
      </div>

      {/* Footer — next lesson CTA */}
      {nextLesson && (
        <div className="rounded-2xl border border-slate-200 bg-white p-5 flex items-center justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-slate-500">
              Next in {lesson.chapter}
            </p>
            <p className="mt-1 text-base font-semibold text-slate-900">
              {nextLesson.title}
            </p>
          </div>
          <Link
            href={`/student/lesson/${nextLesson.id}`}
            className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 shrink-0"
          >
            Continue
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      )}
    </div>
  );
}

// ----------------- Sub-components -----------------

function Pill({
  icon: Icon,
  text,
}: {
  icon: typeof Clock;
  text: string;
}) {
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700">
      <Icon className="h-3 w-3" />
      {text}
    </span>
  );
}

function ResourceLink({
  icon: Icon,
  label,
  hint,
  available,
}: {
  icon: typeof PlayCircle;
  label: string;
  hint: string;
  available: boolean;
}) {
  return (
    <div
      className={`flex items-start gap-3 rounded-lg border px-3 py-2.5 ${
        available
          ? "border-slate-200 bg-white"
          : "border-dashed border-slate-200 bg-slate-50"
      }`}
    >
      <Icon
        className={`h-4 w-4 mt-0.5 shrink-0 ${
          available ? "text-indigo-600" : "text-slate-300"
        }`}
      />
      <div className="min-w-0 flex-1">
        <p
          className={`text-sm font-medium ${
            available ? "text-slate-900" : "text-slate-500"
          }`}
        >
          {label}
        </p>
        <p className="text-xs text-slate-500 mt-0.5">{hint}</p>
      </div>
      {!available && (
        <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 shrink-0">
          Soon
        </span>
      )}
    </div>
  );
}



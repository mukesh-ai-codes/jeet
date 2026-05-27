"use client";

/**
 * MarkAsStartedButton — first real engagement event in the JEET retention loop.
 *
 * Behavior:
 *   - On mount, reads localStorage to see if this lesson was already started
 *     (avoids duplicate event rows on the same lesson).
 *   - On click, optimistically flips UI to "Started" before the network call.
 *   - POSTs lesson_started event with source="lesson_detail_page" so we can
 *     later analyze: do students start more from daily-plan or related-list?
 *   - On API failure, reverts UI and shows error toast.
 *
 * localStorage shape: JSON map of { [lesson_id]: ISO_timestamp }
 * Keyed by lesson_id; value is when we marked it started locally.
 * In a future polish pass we'd query events table instead of localStorage,
 * but for Day 13 this is a clean shortcut that survives page refresh.
 */

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { CheckCircle2, Loader2, Play } from "lucide-react";

import { studentApi, getErrorMessage } from "@/lib/api";

const STORAGE_KEY = "jeet_started_lessons_v1";

type StartedMap = Record<string, string>;

function readStartedMap(): StartedMap {
  if (typeof window === "undefined") return {};
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function writeStartedMap(map: StartedMap): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(map));
  } catch {
    // Quota or private-mode failures are non-fatal
  }
}

export default function MarkAsStartedButton({
  lessonId,
  chapterName,
}: {
  lessonId: string;
  chapterName?: string;
}) {
  const [started, setStarted] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // On mount, hydrate from localStorage so refresh keeps the state
  useEffect(() => {
    const map = readStartedMap();
    if (map[lessonId]) setStarted(true);
  }, [lessonId]);

  async function handleStart() {
    if (started || submitting) return;

    setSubmitting(true);
    // Optimistic flip
    setStarted(true);

    try {
      await studentApi.trackLessonEvent(lessonId, "lesson_started", {
        source: "lesson_detail_page",
        chapter: chapterName,
      });

      // Persist locally
      const map = readStartedMap();
      map[lessonId] = new Date().toISOString();
      writeStartedMap(map);

      toast.success("Lesson started. Tracked.", {
        description: "JEET is logging this to your engagement signal.",
      });
    } catch (err) {
      // Revert optimistic UI
      setStarted(false);
      toast.error("Couldn't track that.", {
        description: getErrorMessage(err),
      });
    } finally {
      setSubmitting(false);
    }
  }

  if (started) {
    return (
      <div className="w-full inline-flex items-center justify-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-semibold text-emerald-700">
        <CheckCircle2 className="h-4 w-4" />
        Lesson started — tracked
      </div>
    );
  }

  return (
    <button
      type="button"
      onClick={handleStart}
      disabled={submitting}
      className="w-full inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-3 text-sm font-semibold text-white hover:bg-indigo-700 disabled:bg-indigo-400 transition"
    >
      {submitting ? (
        <>
          <Loader2 className="h-4 w-4 animate-spin" />
          Starting…
        </>
      ) : (
        <>
          <Play className="h-4 w-4" />
          Start lesson
        </>
      )}
    </button>
  );
}

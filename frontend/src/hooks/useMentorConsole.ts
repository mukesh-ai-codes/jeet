"use client";

/**
 * useMentorConsole — drives the Coach Console.
 *
 * Loads cohorts + at-risk list in parallel on mount.
 * Lazily fetches Whisper data for a selected student (and caches per session).
 * Exposes a refresh() so the queue updates after a logged intervention.
 */

import { useCallback, useEffect, useState } from "react";
import { mentorApi, getErrorMessage } from "@/lib/api";
import type {
  MentorCohort,
  AtRiskListResponse,
  StudentWhisperResponse,
} from "@/types";

type State = {
  cohorts: MentorCohort[];
  queue: AtRiskListResponse | null;
  loading: boolean;
  error: string | null;
};

export function useMentorConsole() {
  const [state, setState] = useState<State>({
    cohorts: [],
    queue: null,
    loading: true,
    error: null,
  });

  const [whisperCache, setWhisperCache] = useState<Record<string, StudentWhisperResponse>>({});

  const fetchAll = useCallback(async () => {
    setState((s) => ({ ...s, loading: true, error: null }));
    const [cohortsRes, queueRes] = await Promise.allSettled([
      mentorApi.getCohorts(),
      mentorApi.getAtRiskStudents(),
    ]);

    setState({
      cohorts: cohortsRes.status === "fulfilled" ? cohortsRes.value.cohorts : [],
      queue: queueRes.status === "fulfilled" ? queueRes.value : null,
      loading: false,
      error:
        cohortsRes.status === "rejected"
          ? getErrorMessage(cohortsRes.reason)
          : queueRes.status === "rejected"
          ? getErrorMessage(queueRes.reason)
          : null,
    });
  }, []);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  const getWhisper = useCallback(
    async (studentId: string): Promise<StudentWhisperResponse | null> => {
      if (whisperCache[studentId]) return whisperCache[studentId];
      try {
        const data = await mentorApi.getStudentWhisper(studentId);
        setWhisperCache((c) => ({ ...c, [studentId]: data }));
        return data;
      } catch {
        return null;
      }
    },
    [whisperCache]
  );

  return {
    ...state,
    getWhisper,
    refresh: fetchAll,
  };
}

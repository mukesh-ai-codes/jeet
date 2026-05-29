"use client";

/**
 * useParentDashboard — manages the parent's children list, the selected
 * child, and that child's dashboard.
 *
 * Flow:
 *   1. Fetch children list on mount
 *   2. Auto-select the first child
 *   3. Fetch the selected child's dashboard
 *   4. selectChild(id) switches the active child and refetches
 *
 * Returns childrenLoading and dashboardLoading separately so the UI can
 * show the child picker immediately while the dashboard panel loads.
 */

import { useCallback, useEffect, useState } from "react";

import { parentApi, getErrorMessage } from "@/lib/api";
import type { ChildSummary, ParentDashboard } from "@/types";

type UseParentDashboardReturn = {
  children: ChildSummary[];
  selectedChildId: string | null;
  selectChild: (id: string) => void;
  dashboard: ParentDashboard | null;
  childrenLoading: boolean;
  dashboardLoading: boolean;
  error: string | null;
};

export function useParentDashboard(): UseParentDashboardReturn {
  const [children, setChildren] = useState<ChildSummary[]>([]);
  const [selectedChildId, setSelectedChildId] = useState<string | null>(null);
  const [dashboard, setDashboard] = useState<ParentDashboard | null>(null);
  const [childrenLoading, setChildrenLoading] = useState(true);
  const [dashboardLoading, setDashboardLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 1. Load children on mount
  useEffect(() => {
    let cancelled = false;
    async function loadChildren() {
      setChildrenLoading(true);
      setError(null);
      try {
        const res = await parentApi.getChildren();
        if (cancelled) return;
        setChildren(res.children);
        if (res.children.length > 0) {
          setSelectedChildId(res.children[0].student_user_id);
        }
      } catch (err) {
        if (!cancelled) setError(getErrorMessage(err));
      } finally {
        if (!cancelled) setChildrenLoading(false);
      }
    }
    loadChildren();
    return () => {
      cancelled = true;
    };
  }, []);

  // 2. Load dashboard whenever selected child changes
  useEffect(() => {
    if (!selectedChildId) return;
    let cancelled = false;
    async function loadDashboard() {
      setDashboardLoading(true);
      setError(null);
      try {
        const data = await parentApi.getChildDashboard(selectedChildId!);
        if (cancelled) return;
        setDashboard(data);
      } catch (err) {
        if (!cancelled) setError(getErrorMessage(err));
      } finally {
        if (!cancelled) setDashboardLoading(false);
      }
    }
    loadDashboard();
    return () => {
      cancelled = true;
    };
  }, [selectedChildId]);

  const selectChild = useCallback((id: string) => {
    setSelectedChildId(id);
  }, []);

  return {
    children,
    selectedChildId,
    selectChild,
    dashboard,
    childrenLoading,
    dashboardLoading,
    error,
  };
}

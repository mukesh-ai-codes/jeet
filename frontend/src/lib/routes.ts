/**
 * Centralized route-redirect logic.
 *
 * Given a user, figure out where they should land. This is the single place
 * the role-based routing decisions live — login page, protected route, and
 * onboarding "Finish" all defer to these helpers.
 */

import type { AuthUser, UserRole } from "@/types";

// Dashboard home for each role (post-onboarding).
const DASHBOARD_BY_ROLE: Record<UserRole, string> = {
  admin: "/admin",
  mentor: "/mentor",
  student: "/student",
  parent: "/parent",
};

// Onboarding flow for each role (when is_onboarded === false).
// Day 12 only builds the admin wizard; others stub to their dashboard.
const ONBOARDING_BY_ROLE: Record<UserRole, string> = {
  admin: "/onboarding/admin",
  mentor: "/mentor",   // Day 14 will add /onboarding/mentor
  student: "/student", // Day 13 will add /onboarding/student
  parent: "/parent",   // Day 14 will add /onboarding/parent
};

export function landingPathFor(user: AuthUser): string {
  if (!user.is_onboarded) {
    return ONBOARDING_BY_ROLE[user.role];
  }
  return DASHBOARD_BY_ROLE[user.role];
}

export function dashboardPathFor(role: UserRole): string {
  return DASHBOARD_BY_ROLE[role];
}

export function isAllowedOnPath(user: AuthUser, allowedRoles: UserRole[]): boolean {
  return allowedRoles.includes(user.role);
}

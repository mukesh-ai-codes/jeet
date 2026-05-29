/**
 * Day 16: the backend now sends the REAL risk_tier on the student dashboard
 * (computed the same way as the mentor's view), so we no longer derive it
 * client-side. This file now does ONE small job: soften the real tier for the
 * student's OWN screen.
 *
 * Why soften? Mentors and parents should see the truth ("urgent"). But a
 * student opening their own home screen should never be greeted by a blaring
 * "URGENT" — that's demotivating, the opposite of retention. So we map the
 * real tier down one notch for the student view only.
 *
 * The real tier is still what the backend stores and what mentors/parents see.
 * We return a RiskTier so the existing WelcomeHeader / RiskChip keep working
 * with zero changes — we just feed them a gentler value.
 */

import type { RiskTier } from "@/types";

/** Map the real backend tier -> a gentler tier for the student's own view. */
export function softenTierForStudent(tier: RiskTier | undefined | null): RiskTier {
  switch (tier) {
    case "urgent":
      return "critical";  // still serious, but not alarm-red on a kid's home screen
    case "critical":
      return "watch";
    case "watch":
      return "watch";
    case "lost":
      return "lost";
    case "stable":
    default:
      return "stable";
  }
}

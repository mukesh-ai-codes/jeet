#!/usr/bin/env python3
"""
Day 16 frontend patch (revised — keeps WelcomeHeader prop unchanged):
  1. Add risk_tier + risk_score to the StudentDashboard TS interface.
  2. In student/page.tsx: stop deriving; read real dashboard.risk_tier,
     soften it, and pass it as the SAME riskTier prop (no component rewrite).

Safe + idempotent. riskDerive.ts is replaced separately (full-file paste).
"""
from pathlib import Path

# ---- FILE 1: types/index.ts ------------------------------------------------
types = Path("frontend/src/types/index.ts")
t = types.read_text()

TYPE_ANCHOR = """  recent_assessments: Array<{
    title: string;
    subject: string;
    chapter?: string;
    score: number;
    max_score: number;
    percentage: number;
    submitted_at: string;
  }>;
}"""

TYPE_NEW = """  recent_assessments: Array<{
    title: string;
    subject: string;
    chapter?: string;
    score: number;
    max_score: number;
    percentage: number;
    submitted_at: string;
  }>;
  risk_tier: RiskTier;
  risk_score: number;
}"""

if "risk_tier: RiskTier;" in t:
    print("\u2713 TS type already patched")
elif TYPE_ANCHOR not in t:
    print("\u2717 TS type anchor not found \u2014 aborting, no write")
    raise SystemExit(1)
else:
    t = t.replace(TYPE_ANCHOR, TYPE_NEW, 1)
    if "type RiskTier" not in t:
        t = t.replace(
            "export interface StudentDashboard {",
            'export type RiskTier = "stable" | "watch" | "critical" | "urgent" | "lost";\n\nexport interface StudentDashboard {',
            1,
        )
        print("  (added RiskTier type definition)")
    types.write_text(t)
    print("\u2713 TS type: added risk_tier + risk_score")

# ---- FILE 2: student/page.tsx ----------------------------------------------
page = Path("frontend/src/app/student/page.tsx")
p = page.read_text()

OLD_IMPORT = 'import { deriveRisk } from "@/lib/riskDerive";'
NEW_IMPORT = 'import { softenTierForStudent } from "@/lib/riskDerive";'
OLD_USE = "  const riskTier = deriveRisk(data.dashboard);"
NEW_USE = "  const riskTier = softenTierForStudent(data.dashboard?.risk_tier);"

if "softenTierForStudent" in p:
    print("\u2713 page.tsx already patched")
else:
    for old in (OLD_IMPORT, OLD_USE):
        if old not in p:
            print(f"\u2717 page.tsx anchor not found: {old!r} \u2014 aborting")
            raise SystemExit(1)
    p = p.replace(OLD_IMPORT, NEW_IMPORT, 1).replace(OLD_USE, NEW_USE, 1)
    page.write_text(p)
    print("\u2713 page.tsx: uses real tier (softened), WelcomeHeader unchanged")

print("\nDone. The riskTier prop still flows into WelcomeHeader as before.")

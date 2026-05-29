#!/usr/bin/env python3
"""
Day 16 patch: surface REAL risk_tier on the student dashboard.

Adds risk_tier + risk_score to:
  1. StudentDashboard Pydantic schema (backend/app/schemas/student.py)
  2. The dashboard handler (backend/app/api/students.py) — computed from the
     v_student_features row already in scope, using the SAME tier logic as
     v_at_risk_students so mentor + student views never disagree.

Safe:
  - Anchored str.replace; refuses to write if an anchor is missing.
  - Idempotent: re-running is a no-op.
"""
from pathlib import Path

# ---------------------------------------------------------------------------
# FILE 1: schema — add two fields to StudentDashboard
# ---------------------------------------------------------------------------
schema = Path("backend/app/schemas/student.py")
s = schema.read_text()

SCHEMA_ANCHOR = """    assessments: AssessmentSummaryBlock
    recent_assessments: List[RecentAssessment]"""

SCHEMA_NEW = """    assessments: AssessmentSummaryBlock
    recent_assessments: List[RecentAssessment]
    risk_tier: str    # real backend tier: stable|watch|critical|urgent|lost
    risk_score: float # 0-100, same scale as the mentor view"""

if "risk_tier: str" in s and "recent_assessments: List[RecentAssessment]\n    risk_tier" in s:
    print("✓ schema already patched")
elif SCHEMA_ANCHOR not in s:
    print("✗ schema anchor not found — aborting, no write")
    raise SystemExit(1)
else:
    schema.write_text(s.replace(SCHEMA_ANCHOR, SCHEMA_NEW, 1))
    print("✓ schema: added risk_tier + risk_score to StudentDashboard")

# ---------------------------------------------------------------------------
# FILE 2: handler — compute tier from the row, pass into StudentDashboard(...)
# ---------------------------------------------------------------------------
handler = Path("backend/app/api/students.py")
h = handler.read_text()

# (a) Insert the tier computation right before "# 5. Compose response"
COMPUTE_ANCHOR = "    # 5. Compose response\n    return StudentDashboard("

COMPUTE_NEW = '''    # 4b. Compute real risk tier/score — SAME logic as v_at_risk_students,
    #     so the student's own view never disagrees with the mentor's view.
    _score_drop = float(row["avg_score_pct"]) - float(row["recent_avg_score_pct"])
    _avg = float(row["avg_score_pct"])
    _fa = int(row["failed_assessments"])
    _fp = int(row["failed_payments"])
    _vol = float(row["score_volatility"])
    _comp = float(row["lesson_completion_rate"])
    _att = float(row["attendance_rate"])
    _dsl = float(row["days_since_last_login"])
    _status = row["enrollment_status"]

    _risk_score = min(100.0, max(0.0,
        min(30.0, max(0.0, _score_drop) * 3.0)
        + min(24.0, _fa * 6.0)
        + min(24.0, _fp * 12.0)
        + min(15.0, max(0.0, _vol - 10.0))
        + (12.0 if _avg < 35 else 0.0)
        + (8.0 if _comp < 0.4 else 0.0)
        + (8.0 if _att < 0.5 else 0.0)
        + min(10.0, _dsl * 0.5)
    ))

    if _status in ("churned", "cancelled"):
        _risk_tier = "lost"
    elif (_fp >= 1 and _score_drop >= 10) or (_avg < 35 and _score_drop >= 10) or _fa >= 4:
        _risk_tier = "urgent"
    elif _score_drop >= 10 or _fa >= 2 or _comp < 0.4 or _fp >= 1:
        _risk_tier = "critical"
    elif _vol > 15 or _fa >= 1 or _score_drop >= 5 or _att < 0.5:
        _risk_tier = "watch"
    else:
        _risk_tier = "stable"

    # 5. Compose response
    return StudentDashboard('''

# (b) Add the two kwargs to the StudentDashboard(...) call, right after
#     the recent_assessments list closes: "        ],\n    )\n"
RETURN_ANCHOR = """            for r in recent_rows
        ],
    )"""

RETURN_NEW = """            for r in recent_rows
        ],
        risk_tier=_risk_tier,
        risk_score=round(_risk_score, 1),
    )"""

if "_risk_tier = " in h:
    print("✓ handler already patched")
else:
    if COMPUTE_ANCHOR not in h or RETURN_ANCHOR not in h:
        print("✗ handler anchor not found — aborting, no write")
        raise SystemExit(1)
    h = h.replace(COMPUTE_ANCHOR, COMPUTE_NEW, 1)
    h = h.replace(RETURN_ANCHOR, RETURN_NEW, 1)
    handler.write_text(h)
    print("✓ handler: computes real risk_tier + risk_score, passes into response")

print("\\nDone. Restart-safe (uvicorn --reload will pick it up).")

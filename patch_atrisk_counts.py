#!/usr/bin/env python3
"""
Day 16 patch: fix at-risk summary counts in mentors.py

PROBLEM:
  urgent/critical/watch counts were computed by looping over `rows`, which is
  capped at LIMIT 50 and sorted by risk_score DESC. So the summary strip
  described only the worst 50 students, not the mentor's true at-risk population.
  Result: counts didn't match reality (showed 21 urgent vs true 30), and 'watch'
  students were invisible because they never made the top 50.

FIX:
  1. Compute the four counts from a SEPARATE aggregate query over the FULL
     at-risk set (same WHERE clause, no LIMIT) -> strip always tells the truth.
  2. Raise the queue display cap 50 -> 100 so watch-tier students are reachable.
  3. total_at_risk now reflects the full population, not len(rows).

SAFETY:
  - API response shape (AtRiskListResponse) unchanged.
  - The student list still respects the cap (focused triage queue).
  - Idempotent: re-running is a no-op (guard matches the new aggregate marker).

Run from repo root:  python3 patch_atrisk_counts.py
"""
from pathlib import Path

TARGET = Path("backend/app/api/mentors.py")

OLD_BLOCK = '''    rows = db.execute(text(f"""
        SELECT *
        FROM v_at_risk_students
        WHERE {where_clause}
          AND risk_tier IN ('urgent', 'critical', 'watch')
        ORDER BY risk_score DESC
        LIMIT :limit
    """), params).mappings().all()

    # Build summary counts
    urgent = sum(1 for r in rows if r["risk_tier"] == "urgent")
    critical = sum(1 for r in rows if r["risk_tier"] == "critical")
    watch = sum(1 for r in rows if r["risk_tier"] == "watch")

    return AtRiskListResponse(
        total_at_risk=len(rows),
        urgent_count=urgent,
        critical_count=critical,
        watch_count=watch,'''

NEW_BLOCK = '''    # Summary counts: computed over the FULL at-risk population (no LIMIT) so the
    # mentor's summary strip is always truthful, independent of the display cap.
    count_rows = db.execute(text(f"""
        SELECT risk_tier, COUNT(*) AS n
        FROM v_at_risk_students
        WHERE {where_clause}
          AND risk_tier IN ('urgent', 'critical', 'watch')
        GROUP BY risk_tier
    """), params).mappings().all()
    counts = {cr["risk_tier"]: int(cr["n"]) for cr in count_rows}
    urgent = counts.get("urgent", 0)
    critical = counts.get("critical", 0)
    watch = counts.get("watch", 0)
    total_at_risk = urgent + critical + watch

    # Display queue: focused triage list, capped. Worst-first by risk score.
    rows = db.execute(text(f"""
        SELECT *
        FROM v_at_risk_students
        WHERE {where_clause}
          AND risk_tier IN ('urgent', 'critical', 'watch')
        ORDER BY risk_score DESC
        LIMIT :limit
    """), params).mappings().all()

    return AtRiskListResponse(
        total_at_risk=total_at_risk,
        urgent_count=urgent,
        critical_count=critical,
        watch_count=watch,'''


def main() -> None:
    if not TARGET.exists():
        print(f"✗ {TARGET} not found. Run from repo root (~/Projects/jeet).")
        return

    text_src = TARGET.read_text()

    # Idempotency: the new aggregate query introduces this exact marker line.
    if "SELECT risk_tier, COUNT(*) AS n" in text_src:
        print("✓ Already patched (full-population counts present). No changes made.")
        return

    if OLD_BLOCK not in text_src:
        print("✗ Anchor block not found — file may have changed. Aborting (no write).")
        print("  Expected to find the 'Build summary counts' loop block.")
        return

    patched = text_src.replace(OLD_BLOCK, NEW_BLOCK, 1)
    TARGET.write_text(patched)
    print("✓ Patched mentors.py: counts now full-population, queue cap 50 -> 100.")
    print("  Next: also bump the default `limit` param to 100 if it's set to 50.")


if __name__ == "__main__":
    main()

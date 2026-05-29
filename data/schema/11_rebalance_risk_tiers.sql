-- ============================================================================
-- Migration: 11_rebalance_risk_tiers.sql
-- Day 16 — Risk-tier rebalance
--
-- PROBLEM (pre-Day-16):
--   v_at_risk_students.risk_tier led with `days_since_last_login > 14 -> urgent`.
--   In the current synthetic dataset the simulation clock is frozen in the past,
--   so EVERY active student is idle 14+ days. That single condition short-circuited
--   the CASE and bucketed all 2,079 active students as 'urgent'. critical/watch = 0.
--   A retention OS whose risk tiers don't discriminate is not demonstrating intelligence.
--
-- FIX:
--   Re-tier on signals that ACTUALLY vary in the data:
--     - academic decline  (recent_avg_score_pct vs avg_score_pct)   ~1262 students
--     - failed assessments (>= 2)                                    ~752 students
--     - score volatility   (> 15)                                    ~577 students
--     - failed payments    (>= 1)                                    ~156 students
--     - low completion / low absolute score                          (tail)
--   days_since_last_login is DEMOTED: removed from tiering (degenerate here),
--   kept only as a small additive nudge in risk_score so the number still moves.
--   When the sim clock is fixed (Day 26), idle-time becomes meaningful again and
--   can re-enter the score weighting -- but tiering must never hinge on one signal.
--
-- CONTRACT SAFETY:
--   Column list and names are IDENTICAL to the previous view. risk_score stays
--   0-100 numeric; risk_tier stays one of lost|urgent|critical|watch|stable.
--   No application code or API schema changes. mentors.py / interventions.py /
--   analytics.py continue to read the same columns.
--
-- Apply:  psql -U mj -d jeet_dev -f data/schema/11_rebalance_risk_tiers.sql
-- ============================================================================

CREATE OR REPLACE VIEW v_at_risk_students AS
WITH scored AS (
    SELECT
        sf.student_user_id,
        sf.full_name,
        sf.grade,
        sf.target_exam,
        sf.program_slug,
        sf.days_since_last_login,
        sf.lesson_completion_rate,
        sf.avg_score_pct,
        sf.recent_avg_score_pct,
        sf.score_volatility,
        sf.attendance_rate,
        sf.failed_assessments,
        sf.late_night_logins,
        sf.failed_payments,
        sf.enrollment_status,

        -- Academic decline: how many points recent scores have dropped vs the
        -- student's own historical average. Positive = getting worse.
        (sf.avg_score_pct - sf.recent_avg_score_pct) AS score_drop,

        -- ----------------------------------------------------------------
        -- risk_score: 0-100, weighted by signals that actually vary.
        -- Each term is bounded so no single signal can dominate the way
        -- days_since_last_login did before.
        -- ----------------------------------------------------------------
        LEAST(100::numeric, GREATEST(0::numeric,
              -- academic decline: up to ~30 pts (3 per pt dropped, capped)
              LEAST(30::numeric, GREATEST(0::numeric, (sf.avg_score_pct - sf.recent_avg_score_pct)) * 3::numeric)
              -- failed assessments: 6 each, capped at 24
            + LEAST(24::numeric, sf.failed_assessments * 6::numeric)
              -- failed payments: 12 each, capped at 24 (commercial churn signal)
            + LEAST(24::numeric, sf.failed_payments * 12::numeric)
              -- volatility: up to ~15 pts
            + LEAST(15::numeric, GREATEST(0::numeric, sf.score_volatility - 10::numeric))
              -- low absolute performance
            + CASE WHEN sf.avg_score_pct < 35::numeric THEN 12 ELSE 0 END::numeric
            + CASE WHEN sf.lesson_completion_rate < 0.4 THEN 8  ELSE 0 END::numeric
            + CASE WHEN sf.attendance_rate < 0.5      THEN 8  ELSE 0 END::numeric
              -- idle time DEMOTED to a small nudge (0.5/day, capped at 10)
            + LEAST(10::numeric, sf.days_since_last_login * 0.5::numeric)
        )) AS risk_score,

        -- ----------------------------------------------------------------
        -- risk_tier: ordered most-severe first. Built on varying signals.
        -- ----------------------------------------------------------------
        CASE
            WHEN sf.enrollment_status = ANY (ARRAY['churned'::text, 'cancelled'::text])
                THEN 'lost'::text

            -- URGENT: stacked hard-failure. Commercial + academic, or academic collapse.
            WHEN (sf.failed_payments >= 1 AND (sf.avg_score_pct - sf.recent_avg_score_pct) >= 10)
              OR (sf.avg_score_pct < 35::numeric AND (sf.avg_score_pct - sf.recent_avg_score_pct) >= 10)
              OR (sf.failed_assessments >= 4)
                THEN 'urgent'::text

            -- CRITICAL: one strong signal firing. Intervene this week.
            WHEN ((sf.avg_score_pct - sf.recent_avg_score_pct) >= 10)
              OR (sf.failed_assessments >= 2)
              OR (sf.lesson_completion_rate < 0.4)
              OR (sf.failed_payments >= 1)
                THEN 'critical'::text

            -- WATCH: early wobble. Keep an eye on.
            WHEN (sf.score_volatility > 15::numeric)
              OR (sf.failed_assessments >= 1)
              OR ((sf.avg_score_pct - sf.recent_avg_score_pct) >= 5)
              OR (sf.attendance_rate < 0.5)
                THEN 'watch'::text

            ELSE 'stable'::text
        END AS risk_tier

    FROM v_student_features sf
    WHERE sf.enrollment_status = 'active'::text
)
SELECT
    student_user_id,
    full_name,
    grade,
    target_exam,
    program_slug,
    days_since_last_login,
    lesson_completion_rate,
    avg_score_pct,
    attendance_rate,
    failed_assessments,
    late_night_logins,
    failed_payments,
    enrollment_status,
    round(risk_score, 1) AS risk_score,
    risk_tier
FROM scored;

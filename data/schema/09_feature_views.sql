-- ============================================================
-- JEET DATABASE — ML FEATURE VIEWS
-- ============================================================
-- Materialized + regular views that aggregate behavior into
-- ML-ready features per student. The ML pipeline reads from
-- these — never from raw event tables.
--
-- This is the "feature store" layer of JEET.
-- ============================================================

-- ============================================================
-- VIEW 1: Student Features (one row per student, ~40 columns)
-- The MAIN feature source for ML training
-- ============================================================
DROP MATERIALIZED VIEW IF EXISTS v_student_features CASCADE;

CREATE MATERIALIZED VIEW v_student_features AS
WITH
-- Login activity aggregates
login_stats AS (
    SELECT
        user_id,
        COUNT(*) AS total_logins,
        COUNT(DISTINCT DATE(created_at)) AS unique_active_days,
        MAX(created_at) AS last_login_at,
        MIN(created_at) AS first_login_at,
        COUNT(*) FILTER (WHERE EXTRACT(DOW FROM created_at) = 0) AS sunday_logins,
        COUNT(*) FILTER (WHERE EXTRACT(HOUR FROM created_at) BETWEEN 23 AND 23
                          OR EXTRACT(HOUR FROM created_at) BETWEEN 0 AND 2) AS late_night_logins
    FROM events
    WHERE event_type = 'user_login'
    GROUP BY user_id
),
-- Lesson activity
lesson_stats AS (
    SELECT
        user_id,
        COUNT(*) FILTER (WHERE event_type = 'lesson_started') AS lessons_started,
        COUNT(*) FILTER (WHERE event_type = 'lesson_completed') AS lessons_completed,
        COUNT(*) FILTER (WHERE event_type = 'lesson_abandoned') AS lessons_abandoned,
        COUNT(*) FILTER (WHERE event_type = 'lesson_replayed') AS lessons_replayed,
        COUNT(*) FILTER (WHERE event_type = 'notes_downloaded') AS notes_downloaded
    FROM events
    WHERE event_type LIKE 'lesson_%' OR event_type = 'notes_downloaded'
    GROUP BY user_id
),
-- Quiz/Assessment patterns
quiz_event_stats AS (
    SELECT
        user_id,
        COUNT(*) FILTER (WHERE event_type IN ('quiz_started', 'mock_test_started')) AS quizzes_started,
        COUNT(*) FILTER (WHERE event_type IN ('quiz_submitted', 'mock_test_submitted')) AS quizzes_submitted,
        COUNT(*) FILTER (WHERE event_type IN ('quiz_abandoned', 'mock_test_abandoned')) AS quizzes_abandoned
    FROM events
    WHERE event_type LIKE 'quiz_%' OR event_type LIKE 'mock_test_%'
    GROUP BY user_id
),
-- Assessment scores (from assessments table)
assessment_scores AS (
    SELECT
        student_user_id AS user_id,
        COUNT(*) AS total_assessments,
        AVG(percentage) AS avg_score_pct,
        STDDEV(percentage) AS score_stddev,
        MAX(percentage) AS best_score_pct,
        MIN(percentage) AS worst_score_pct,
        COUNT(*) FILTER (WHERE percentage < 40) AS failed_assessments,
        COUNT(*) FILTER (WHERE percentage >= 75) AS strong_assessments,
        -- Last quartile performance trend
        AVG(percentage) FILTER (
            WHERE submitted_at >= NOW() - INTERVAL '30 days'
        ) AS recent_avg_score_pct
    FROM assessments
    GROUP BY student_user_id
),
-- Doubt asking patterns
doubt_stats AS (
    SELECT
        user_id,
        COUNT(*) FILTER (WHERE event_type = 'doubt_asked_tutor') AS doubts_to_tutor,
        COUNT(*) FILTER (WHERE event_type = 'doubt_asked_mentor') AS doubts_to_mentor,
        COUNT(*) FILTER (WHERE event_type = 'doubt_resolved') AS doubts_resolved
    FROM events
    WHERE event_type LIKE 'doubt_%'
    GROUP BY user_id
),
-- Attendance (live sessions)
attendance_stats AS (
    SELECT
        e.student_user_id AS user_id,
        COUNT(*) AS sessions_scheduled,
        COUNT(*) FILTER (WHERE a.joined = TRUE) AS sessions_attended,
        AVG(a.duration_minutes) FILTER (WHERE a.joined = TRUE) AS avg_session_duration,
        AVG(a.engagement_score) FILTER (WHERE a.joined = TRUE) AS avg_engagement_score
    FROM attendance a
    JOIN enrollments e ON e.id = a.enrollment_id
    GROUP BY e.student_user_id
),
-- Payment health (parent-side signal)
payment_health AS (
    SELECT
        s.student_user_id AS user_id,
        COUNT(p.id) AS total_payment_attempts,
        COUNT(p.id) FILTER (WHERE p.status = 'captured') AS successful_payments,
        COUNT(p.id) FILTER (WHERE p.status = 'failed') AS failed_payments,
        SUM(p.amount_inr) FILTER (WHERE p.status = 'captured') AS total_paid_inr,
        MAX(p.paid_at) AS last_payment_at
    FROM subscriptions s
    LEFT JOIN payments p ON p.subscription_id = s.id
    GROUP BY s.student_user_id
),
-- Login continuity (the streak / gap signal — predictor of churn)
login_continuity AS (
    SELECT
        user_id,
        EXTRACT(DAY FROM (NOW() - MAX(created_at))) AS days_since_last_login,
        COUNT(DISTINCT DATE(created_at)) * 1.0
            / GREATEST(1, EXTRACT(DAY FROM (MAX(created_at) - MIN(created_at))) + 1)
            AS active_day_ratio
    FROM events
    WHERE event_type = 'user_login'
    GROUP BY user_id
)
SELECT
    -- Identity & profile
    u.id::text                              AS student_user_id,
    u.full_name,
    up.grade,
    up.target_exam::text                    AS target_exam,
    up.daily_study_hours,
    up.motivation_score,
    array_length(up.weak_subjects, 1)       AS num_weak_subjects,
    array_length(up.reported_challenges, 1) AS num_challenges,

    -- Enrollment status (THE TARGET LABEL for ML)
    e.status::text                          AS enrollment_status,
    e.ended_at                              AS churn_date,
    EXTRACT(DAY FROM (COALESCE(e.ended_at, NOW()) - e.enrolled_at)) AS days_active,
    p.slug                                  AS program_slug,
    p.price_inr                             AS program_price,

    -- Login features
    COALESCE(ls.total_logins, 0)            AS total_logins,
    COALESCE(ls.unique_active_days, 0)      AS unique_active_days,
    COALESCE(ls.sunday_logins, 0)           AS sunday_logins,
    COALESCE(ls.late_night_logins, 0)       AS late_night_logins,
    COALESCE(lc.days_since_last_login, 999) AS days_since_last_login,
    COALESCE(lc.active_day_ratio, 0)        AS active_day_ratio,

    -- Lesson features
    COALESCE(lst.lessons_started, 0)        AS lessons_started,
    COALESCE(lst.lessons_completed, 0)      AS lessons_completed,
    COALESCE(lst.lessons_abandoned, 0)      AS lessons_abandoned,
    COALESCE(lst.lessons_replayed, 0)       AS lessons_replayed,
    COALESCE(lst.notes_downloaded, 0)       AS notes_downloaded,
    CASE WHEN COALESCE(lst.lessons_started, 0) > 0
         THEN ROUND(lst.lessons_completed::numeric / lst.lessons_started, 3)
         ELSE 0 END                          AS lesson_completion_rate,

    -- Quiz events
    COALESCE(qes.quizzes_started, 0)        AS quizzes_started,
    COALESCE(qes.quizzes_submitted, 0)      AS quizzes_submitted,
    COALESCE(qes.quizzes_abandoned, 0)      AS quizzes_abandoned,

    -- Assessment scores
    COALESCE(asc_.total_assessments, 0)     AS total_assessments,
    ROUND(COALESCE(asc_.avg_score_pct, 0)::numeric, 2)        AS avg_score_pct,
    ROUND(COALESCE(asc_.score_stddev, 0)::numeric, 2)         AS score_volatility,
    ROUND(COALESCE(asc_.best_score_pct, 0)::numeric, 2)       AS best_score_pct,
    ROUND(COALESCE(asc_.worst_score_pct, 0)::numeric, 2)      AS worst_score_pct,
    COALESCE(asc_.failed_assessments, 0)    AS failed_assessments,
    COALESCE(asc_.strong_assessments, 0)    AS strong_assessments,
    ROUND(COALESCE(asc_.recent_avg_score_pct, 0)::numeric, 2) AS recent_avg_score_pct,

    -- Doubt patterns
    COALESCE(ds.doubts_to_tutor, 0)         AS doubts_to_tutor,
    COALESCE(ds.doubts_to_mentor, 0)        AS doubts_to_mentor,
    COALESCE(ds.doubts_resolved, 0)         AS doubts_resolved,

    -- Attendance
    COALESCE(at.sessions_scheduled, 0)      AS sessions_scheduled,
    COALESCE(at.sessions_attended, 0)       AS sessions_attended,
    CASE WHEN COALESCE(at.sessions_scheduled, 0) > 0
         THEN ROUND(at.sessions_attended::numeric / at.sessions_scheduled, 3)
         ELSE 0 END                          AS attendance_rate,
    ROUND(COALESCE(at.avg_session_duration, 0)::numeric, 2)  AS avg_session_duration_min,
    ROUND(COALESCE(at.avg_engagement_score, 0)::numeric, 2)  AS avg_engagement_score,

    -- Payment health
    COALESCE(ph.total_payment_attempts, 0)  AS total_payment_attempts,
    COALESCE(ph.successful_payments, 0)     AS successful_payments,
    COALESCE(ph.failed_payments, 0)         AS failed_payments,
    COALESCE(ph.total_paid_inr, 0)          AS total_paid_inr,
    CASE WHEN COALESCE(ph.total_payment_attempts, 0) > 0
         THEN ROUND(ph.successful_payments::numeric / ph.total_payment_attempts, 3)
         ELSE 0 END                          AS payment_success_rate,

    -- Binary churn label (for ML training)
    CASE WHEN e.status IN ('churned', 'cancelled') THEN 1 ELSE 0 END AS is_churned

FROM users u
JOIN user_profiles up ON up.user_id = u.id
JOIN enrollments   e  ON e.student_user_id = u.id
JOIN programs      p  ON p.id = e.program_id
LEFT JOIN login_stats        ls  ON ls.user_id = u.id
LEFT JOIN lesson_stats       lst ON lst.user_id = u.id
LEFT JOIN quiz_event_stats   qes ON qes.user_id = u.id
LEFT JOIN assessment_scores  asc_ ON asc_.user_id = u.id
LEFT JOIN doubt_stats        ds  ON ds.user_id = u.id
LEFT JOIN attendance_stats   at  ON at.user_id = u.id
LEFT JOIN payment_health     ph  ON ph.user_id = u.id
LEFT JOIN login_continuity   lc  ON lc.user_id = u.id
WHERE u.role = 'student';

-- Index for fast lookups
CREATE UNIQUE INDEX idx_v_student_features_user ON v_student_features(student_user_id);
CREATE INDEX idx_v_student_features_churned ON v_student_features(is_churned);


-- ============================================================
-- VIEW 2: Daily Engagement Time-Series
-- One row per (student, day) — for retention curves & survival analysis
-- ============================================================
DROP MATERIALIZED VIEW IF EXISTS v_daily_engagement CASCADE;

CREATE MATERIALIZED VIEW v_daily_engagement AS
SELECT
    e.user_id::text                          AS student_user_id,
    DATE(e.created_at)                       AS activity_date,
    COUNT(*) FILTER (WHERE e.event_type = 'user_login')                     AS logins,
    COUNT(*) FILTER (WHERE e.event_type = 'lesson_completed')               AS lessons_completed,
    COUNT(*) FILTER (WHERE e.event_type IN ('quiz_submitted',
                                            'mock_test_submitted'))         AS quizzes_completed,
    COUNT(*) FILTER (WHERE e.event_type LIKE 'doubt_asked%')                AS doubts_asked,
    COUNT(*) FILTER (WHERE e.event_type = 'lesson_abandoned')               AS lessons_abandoned,
    COUNT(*)                                                                AS total_events
FROM events e
JOIN users u ON u.id = e.user_id
WHERE u.role = 'student'
GROUP BY e.user_id, DATE(e.created_at);

CREATE INDEX idx_v_daily_engagement_student_date
    ON v_daily_engagement(student_user_id, activity_date DESC);
CREATE INDEX idx_v_daily_engagement_date ON v_daily_engagement(activity_date);


-- ============================================================
-- VIEW 3: Cohort Retention (one row per cohort × week-since-start)
-- Powers cohort retention curves in Admin dashboard
-- ============================================================
DROP MATERIALIZED VIEW IF EXISTS v_cohort_retention CASCADE;

CREATE MATERIALIZED VIEW v_cohort_retention AS
WITH cohort_students AS (
    SELECT
        c.id          AS cohort_id,
        c.name        AS cohort_name,
        c.start_date,
        u.id          AS student_user_id,
        e.enrolled_at,
        e.ended_at,
        e.status
    FROM cohorts c
    JOIN enrollments e ON e.cohort_id = c.id
    JOIN users u       ON u.id = e.student_user_id
    WHERE u.role = 'student'
),
week_buckets AS (
    SELECT
        cs.cohort_id,
        cs.cohort_name,
        cs.student_user_id,
        cs.status,
        generate_series(0, 16) AS week_num
    FROM cohort_students cs
)
SELECT
    wb.cohort_id::text,
    wb.cohort_name,
    wb.week_num,
    COUNT(DISTINCT wb.student_user_id) FILTER (
        WHERE wb.status = 'active'
           OR (cs.ended_at IS NOT NULL
               AND wb.week_num * 7 < EXTRACT(DAY FROM cs.ended_at - cs.start_date))
    ) AS active_students,
    COUNT(DISTINCT wb.student_user_id) AS total_cohort_size,
    ROUND(
        COUNT(DISTINCT wb.student_user_id) FILTER (
            WHERE wb.status = 'active'
               OR (cs.ended_at IS NOT NULL
                   AND wb.week_num * 7 < EXTRACT(DAY FROM cs.ended_at - cs.start_date))
        )::numeric * 100.0 / NULLIF(COUNT(DISTINCT wb.student_user_id), 0),
        2
    ) AS retention_pct
FROM week_buckets wb
JOIN cohort_students cs ON cs.student_user_id = wb.student_user_id
                        AND cs.cohort_id = wb.cohort_id
GROUP BY wb.cohort_id, wb.cohort_name, wb.week_num
ORDER BY wb.cohort_id, wb.week_num;

CREATE INDEX idx_v_cohort_retention_cohort ON v_cohort_retention(cohort_id);


-- ============================================================
-- VIEW 4: At-Risk Students (for Mentor Dashboard)
-- Real-time view (not materialized) — always fresh
-- ============================================================
DROP VIEW IF EXISTS v_at_risk_students CASCADE;

CREATE VIEW v_at_risk_students AS
SELECT
    sf.student_user_id,
    sf.full_name,
    sf.grade,
    sf.target_exam,
    sf.program_slug,
    sf.days_since_last_login,
    sf.lesson_completion_rate,
    sf.avg_score_pct,
    sf.attendance_rate,
    sf.failed_assessments,
    sf.late_night_logins,
    sf.failed_payments,
    sf.enrollment_status,

    -- Composite risk score (0-100, higher = more at risk)
    LEAST(100, GREATEST(0,
          (sf.days_since_last_login * 2)
        + (CASE WHEN sf.lesson_completion_rate < 0.4 THEN 15 ELSE 0 END)
        + (CASE WHEN sf.avg_score_pct < 40 THEN 15 ELSE 0 END)
        + (CASE WHEN sf.attendance_rate < 0.5 THEN 12 ELSE 0 END)
        + (sf.failed_assessments * 3)
        + (CASE WHEN sf.late_night_logins > 10 THEN 8 ELSE 0 END)
        + (sf.failed_payments * 10)
    )) AS risk_score,

    -- Risk tier
    CASE
        WHEN sf.enrollment_status IN ('churned', 'cancelled') THEN 'lost'
        WHEN sf.days_since_last_login > 14 OR sf.failed_payments >= 2 THEN 'urgent'
        WHEN sf.days_since_last_login > 7 OR sf.avg_score_pct < 35 THEN 'critical'
        WHEN sf.days_since_last_login > 3 OR sf.attendance_rate < 0.5 THEN 'watch'
        ELSE 'stable'
    END AS risk_tier

FROM v_student_features sf
WHERE sf.enrollment_status = 'active';


-- ============================================================
-- REFRESH FUNCTION — call this to refresh all materialized views
-- ============================================================
CREATE OR REPLACE FUNCTION refresh_jeet_feature_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW v_student_features;
    REFRESH MATERIALIZED VIEW v_daily_engagement;
    REFRESH MATERIALIZED VIEW v_cohort_retention;
    RAISE NOTICE 'JEET feature views refreshed successfully';
END;
$$ LANGUAGE plpgsql;
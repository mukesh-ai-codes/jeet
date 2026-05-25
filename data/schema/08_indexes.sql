-- ============================================================
-- JEET DATABASE — PERFORMANCE INDEXES
-- ============================================================
-- Indexes = lookup tables that make queries 100-1000x faster.
-- Without indexes, finding 1 row in 1M takes seconds.
-- With indexes, it takes microseconds.
-- ============================================================

-- ---------- USERS ----------
CREATE INDEX idx_users_role          ON users(role);
CREATE INDEX idx_users_email_active  ON users(email) WHERE is_active = TRUE;
CREATE INDEX idx_users_created       ON users(created_at DESC);

-- ---------- FAMILIES ----------
CREATE INDEX idx_families_parent     ON families(parent_user_id);
CREATE INDEX idx_families_student    ON families(student_user_id);

-- ---------- ENROLLMENTS ----------
CREATE INDEX idx_enrollments_student     ON enrollments(student_user_id);
CREATE INDEX idx_enrollments_status      ON enrollments(status);
CREATE INDEX idx_enrollments_cohort      ON enrollments(cohort_id);

-- ---------- ATTENDANCE ----------
CREATE INDEX idx_attendance_enrollment_date  ON attendance(enrollment_id, session_date DESC);
CREATE INDEX idx_attendance_session_date     ON attendance(session_date DESC);
CREATE INDEX idx_attendance_joined           ON attendance(joined) WHERE joined = FALSE;

-- ---------- ASSESSMENTS ----------
CREATE INDEX idx_assessments_student_date    ON assessments(student_user_id, submitted_at DESC);
CREATE INDEX idx_assessments_subject         ON assessments(subject_id);

-- ---------- EVENTS (the big table) ----------
CREATE INDEX idx_events_user_created   ON events(user_id, created_at DESC);
CREATE INDEX idx_events_type           ON events(event_type);
CREATE INDEX idx_events_created        ON events(created_at DESC);
-- JSONB index for fast queries on event_data
CREATE INDEX idx_events_data_gin       ON events USING GIN (event_data);

-- ---------- SUBSCRIPTIONS ----------
CREATE INDEX idx_subscriptions_student     ON subscriptions(student_user_id);
CREATE INDEX idx_subscriptions_status      ON subscriptions(status);
CREATE INDEX idx_subscriptions_end_date    ON subscriptions(end_date) WHERE status = 'active';

-- ---------- PAYMENTS ----------
CREATE INDEX idx_payments_subscription  ON payments(subscription_id);
CREATE INDEX idx_payments_status        ON payments(status);
CREATE INDEX idx_payments_paid_at       ON payments(paid_at DESC) WHERE status = 'captured';

-- ---------- RISK_SCORES (queried daily by Sentinel Engine) ----------
CREATE INDEX idx_risk_scores_student_date  ON risk_scores(student_user_id, score_date DESC);
CREATE INDEX idx_risk_scores_tier_date     ON risk_scores(risk_tier, score_date DESC);
CREATE INDEX idx_risk_scores_high_risk     ON risk_scores(score_date DESC)
  WHERE risk_tier IN ('critical', 'urgent');

-- ---------- COHORTS ----------
CREATE INDEX idx_cohorts_mentor      ON cohorts(mentor_user_id);
CREATE INDEX idx_cohorts_active      ON cohorts(is_active) WHERE is_active = TRUE;

-- ============================================================
-- PERFORMANCE NOTES
-- ============================================================
-- Partial indexes (WHERE clauses) save space and speed up
-- the MOST COMMON queries (e.g., active subscriptions only).
--
-- GIN index on JSONB lets you query event_data->>'lesson_id'
-- in milliseconds even with millions of events.
-- ============================================================
-- Day 19: repoint v_at_risk_students at the ML scores table.
-- The model (ml/score_students.py) writes risk_score/risk_tier/reasons into
-- student_risk_scores. This view now reads those instead of the old inline
-- rules formula. Column names unchanged -> every endpoint keeps working.
CREATE OR REPLACE VIEW v_at_risk_students AS
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
    srs.risk_score,
    srs.risk_tier
FROM v_student_features sf
JOIN student_risk_scores srs ON srs.student_user_id = sf.student_user_id
WHERE sf.enrollment_status = 'active';

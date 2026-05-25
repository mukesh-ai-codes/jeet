-- ============================================================
-- JEET DATABASE — AI/ML INTELLIGENCE LAYER
-- ============================================================
-- Table: risk_scores (the Sentinel Engine output)
-- This is where the magic of churn prediction lives.
-- ============================================================

CREATE TABLE risk_scores (
  id                       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  student_user_id          UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  enrollment_id            UUID REFERENCES enrollments(id),

  -- The core prediction
  score_date               DATE NOT NULL,
  churn_probability        NUMERIC(5,4) NOT NULL CHECK (churn_probability BETWEEN 0 AND 1),
  risk_tier                risk_tier NOT NULL,

  -- Time-to-churn (survival model output)
  predicted_churn_date     DATE,  -- NULL if not predicted to churn
  days_to_predicted_churn  INTEGER,
  survival_confidence      NUMERIC(5,4),  -- Confidence of the time prediction

  -- Explainability (SHAP)
  shap_explanations        JSONB NOT NULL DEFAULT '{}'::jsonb,
  -- Example: {"top_factors": [{"feature": "login_continuity", "impact": -0.23}, ...]}

  -- Counterfactuals (DiCE output): "If you do X, risk drops to Y"
  counterfactual_actions   JSONB NOT NULL DEFAULT '[]'::jsonb,
  -- Example: [{"action": "complete_2_physics_sessions", "new_probability": 0.31}, ...]

  -- Intervention tracking
  interventions_triggered  JSONB NOT NULL DEFAULT '[]'::jsonb,
  -- Example: [{"type": "parent_whatsapp", "sent_at": "2026-...", "outcome": "acknowledged"}]

  -- Model versioning (so we can A/B test models)
  model_version            VARCHAR(20) NOT NULL,

  created_at               TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- Only one risk score per student per day
  CONSTRAINT unique_daily_risk_score UNIQUE (student_user_id, score_date)
);

COMMENT ON TABLE risk_scores IS 'Daily snapshots of Sentinel Engine predictions per student';
COMMENT ON COLUMN risk_scores.shap_explanations IS 'Per-prediction feature attribution. Powers mentor talking points.';
COMMENT ON COLUMN risk_scores.counterfactual_actions IS 'What-if analysis from DiCE. Shown in Coach Console.';
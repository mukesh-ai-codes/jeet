#!/usr/bin/env python3
"""JEET Sentinel Engine — SHAP explainer (Day 18).
Turns the churn model's prediction for ONE student into plain-English reasons."""
import os, pickle
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
import shap
pd.set_option('future.no_silent_downcasting', True)

DB_URL = os.environ.get("DATABASE_URL", "postgresql://mj@localhost:5432/jeet_dev")
MODEL_PATH = "ml/artifacts/churn_model.pkl"

FEATURE_COPY = {
    "avg_score_pct":           ("average score is {v:.0f}%", False),
    "recent_avg_score_pct":    ("recent scores have fallen to {v:.0f}%", False),
    "best_score_pct":          ("best score is only {v:.0f}%", False),
    "worst_score_pct":         ("lowest score dropped to {v:.0f}%", False),
    "lesson_completion_rate":  ("only {v:.0%} of lessons completed", False),
    "attendance_rate":         ("attendance is {v:.0%}", False),
    "failed_assessments":      ("{v:.0f} failed assessments", True),
    "strong_assessments":      ("only {v:.0f} strong results", False),
    "score_volatility":        ("scores swinging widely (volatility {v:.0f})", True),
    "failed_payments":         ("{v:.0f} failed payment(s)", True),
    "payment_success_rate":    ("payment success only {v:.0%}", False),
    "avg_engagement_score":    ("low engagement score ({v:.0f})", False),
    "avg_session_duration_min":("short study sessions (~{v:.0f} min)", False),
    "num_weak_subjects":       ("{v:.0f} weak subjects", True),
    "motivation_score":        ("low self-reported motivation ({v:.0f})", False),
    "daily_study_hours":       ("only {v:.1f} study hours/day", False),
}

def load_model():
    with open(MODEL_PATH, "rb") as f:
        b = pickle.load(f)
    return b["model"], b["features"]

def explain_student(row, model, features, explainer, top_n=3):
    X = row[features].fillna(0.0).values.reshape(1, -1)
    risk = float(model.predict_proba(X)[0, 1]) * 100.0
    sv = explainer.shap_values(X)
    sv = (sv[0] if isinstance(sv, list) else sv)
    sv = np.array(sv).flatten()
    contribs = sorted(
        [(features[i], sv[i], row[features[i]]) for i in range(len(features))],
        key=lambda t: t[1], reverse=True)
    no_assessments = float(row.get("total_assessments", 0) or 0) == 0
    score_feats = {"avg_score_pct","best_score_pct","worst_score_pct",
                   "recent_avg_score_pct","score_volatility","failed_assessments",
                   "strong_assessments"}
    reasons = []
    for fname, shap_v, value in contribs:
        if shap_v <= 0 or fname not in FEATURE_COPY:
            continue
        # Don't fabricate "0%" for students who simply have no assessment data.
        if no_assessments and fname in score_feats:
            if "no assessments taken yet" not in reasons:
                reasons.append("no assessments taken yet")
            if len(reasons) >= top_n:
                break
            continue
        tmpl, _ = FEATURE_COPY[fname]
        try:
            reasons.append(tmpl.format(v=float(value)))
        except Exception:
            continue
        if len(reasons) >= top_n:
            break
    return round(risk, 1), reasons

def main():
    engine = create_engine(DB_URL)
    model, features = load_model()
    df = pd.read_sql(text("""
        SELECT * FROM v_student_features
        WHERE enrollment_status = 'active'
        ORDER BY avg_score_pct ASC LIMIT 5"""), engine)
    explainer = shap.TreeExplainer(model)
    print("=" * 60)
    print("SAMPLE EXPLANATIONS (5 lowest-scoring active students)")
    print("=" * 60)
    for _, row in df.iterrows():
        risk, reasons = explain_student(row, model, features, explainer)
        print(f"\n{row.get('full_name','Student')} — churn risk {risk}%")
        for r in (reasons or ["(no upward risk drivers)"]):
            print(f"   • {r}")

if __name__ == "__main__":
    main()

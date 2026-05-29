#!/usr/bin/env python3
"""JEET Sentinel Engine — batch scorer (Day 19).
Scores active students with the model, writes risk + SHAP reasons to
student_risk_scores. v_at_risk_students then reads from this table."""
import os, pickle
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
import shap
pd.set_option('future.no_silent_downcasting', True)

DB_URL = os.environ.get("DATABASE_URL", "postgresql://mj@localhost:5432/jeet_dev")
MODEL_PATH = "ml/artifacts/churn_model.pkl"

FEATURE_COPY = {
    "avg_score_pct":"average score is {v:.0f}%",
    "recent_avg_score_pct":"recent scores have fallen to {v:.0f}%",
    "best_score_pct":"best score is only {v:.0f}%",
    "worst_score_pct":"lowest score dropped to {v:.0f}%",
    "lesson_completion_rate":"only {v:.0%} of lessons completed",
    "attendance_rate":"attendance is {v:.0%}",
    "failed_assessments":"{v:.0f} failed assessments",
    "score_volatility":"scores swinging widely",
    "failed_payments":"{v:.0f} failed payment(s)",
    "avg_engagement_score":"low engagement",
    "avg_session_duration_min":"short study sessions (~{v:.0f} min)",
    "num_weak_subjects":"{v:.0f} weak subjects",
    "motivation_score":"low self-reported motivation",
}
ZERO_SUPPRESS = {"failed_assessments","failed_payments","num_weak_subjects"}
SCORE_FEATS = {"avg_score_pct","best_score_pct","worst_score_pct",
               "recent_avg_score_pct","score_volatility"}

def tier_for(score, status):
    if status in ("churned","cancelled"): return "lost"
    if score >= 50: return "urgent"
    if score >= 25: return "critical"
    if score >= 12: return "watch"
    return "stable"

def reasons_for(row, features, sv, top_n=3):
    no_assess = float(row.get("total_assessments",0) or 0) == 0
    contribs = sorted([(features[i], sv[i], row[features[i]]) for i in range(len(features))],
                      key=lambda t: t[1], reverse=True)
    out = []
    for fname, shap_v, value in contribs:
        if shap_v <= 0 or fname not in FEATURE_COPY: continue
        if no_assess and fname in SCORE_FEATS:
            if "no assessments taken yet" not in out: out.append("no assessments taken yet")
        elif fname in ZERO_SUPPRESS and float(value or 0) == 0:
            continue
        else:
            try: out.append(FEATURE_COPY[fname].format(v=float(value)))
            except Exception: continue
        if len(out) >= top_n: break
    return out

def main():
    engine = create_engine(DB_URL)
    with open(MODEL_PATH,"rb") as f:
        bundle = pickle.load(f)
    model, features = bundle["model"], bundle["features"]
    df = pd.read_sql(text("SELECT * FROM v_student_features WHERE enrollment_status='active'"), engine)
    print(f"Scoring {len(df)} active students ...")
    X = df[features].fillna(0.0)
    proba = model.predict_proba(X)[:,1]*100.0
    explainer = shap.TreeExplainer(model)
    shap_all = explainer.shap_values(X.values)
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS student_risk_scores (
                student_user_id text PRIMARY KEY,
                risk_score numeric NOT NULL,
                risk_tier text NOT NULL,
                reasons text[] NOT NULL DEFAULT '{}',
                scored_at timestamptz NOT NULL DEFAULT now())"""))
        conn.execute(text("TRUNCATE student_risk_scores"))
        rows = []
        for i,(_,row) in enumerate(df.iterrows()):
            score = round(float(proba[i]),1)
            rows.append({"sid":row["student_user_id"],"score":score,
                "tier":tier_for(score,row["enrollment_status"]),
                "reasons":reasons_for(row,features,np.array(shap_all[i]).flatten())})
        for r in rows:
            conn.execute(text("""INSERT INTO student_risk_scores
                (student_user_id,risk_score,risk_tier,reasons)
                VALUES (:sid,:score,:tier,:reasons)"""),
                {"sid":r["sid"],"score":r["score"],"tier":r["tier"],"reasons":r["reasons"]})
    dist = pd.Series([r["tier"] for r in rows]).value_counts()
    print("\nTier distribution:")
    for tier,n in dist.items(): print(f"  {tier:9s} {n}")
    print(f"\nWrote {len(rows)} rows to student_risk_scores.")

if __name__ == "__main__":
    main()

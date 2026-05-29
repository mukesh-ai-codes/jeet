#!/usr/bin/env python3
"""
JEET Sentinel Engine — churn classifier (Day 17).

Trains an XGBoost model to predict student churn from v_student_features.
Prints HONEST metrics (AUC / precision / recall / F1 / confusion matrix) —
not just accuracy, which lies on imbalanced data.

Guards against label leakage:
  - excludes the label (is_churned), the answer (churn_date),
    the giveaway (enrollment_status), and identifiers.
  - prints feature importances so we can SEE if one column is cheating.

Run from repo root with venv active:
  python3 ml/train_churn.py
"""
import os
import pickle
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_auc_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report,
)
import xgboost as xgb

DB_URL = os.environ.get("DATABASE_URL", "postgresql://mj@localhost:5432/jeet_dev")
OUT_DIR = "ml/artifacts"
os.makedirs(OUT_DIR, exist_ok=True)

# Columns that would leak the answer — never feed these to the model.
LEAK_COLS = {
    "is_churned", "churn_date", "enrollment_status",
    "student_user_id", "full_name", "program_slug", "target_exam",
    # ACTIVITY-VOLUME / RECENCY LEAKS: a churned student stops accumulating
    # activity, so these encode WHEN they left, not WHETHER they'll leave.
    "days_active", "total_logins", "unique_active_days", "sunday_logins",
    "late_night_logins", "days_since_last_login", "active_day_ratio",
    "lessons_started", "lessons_completed", "lessons_abandoned",
    "lessons_replayed", "notes_downloaded", "quizzes_started",
    "quizzes_submitted", "quizzes_abandoned", "total_assessments",
    "doubts_to_tutor", "doubts_to_mentor", "doubts_resolved",
    "sessions_scheduled", "sessions_attended",
    "total_payment_attempts", "successful_payments", "total_paid_inr",
}

def main():
    engine = create_engine(DB_URL)
    print("Loading v_student_features ...")
    df = pd.read_sql(text("SELECT * FROM v_student_features"), engine)
    print(f"  {len(df)} rows, {df.shape[1]} columns")

    # Label
    y = df["is_churned"].astype(int)
    print(f"  churned={int(y.sum())}  retained={int((y==0).sum())}  "
          f"(churn rate {y.mean():.1%})")

    # Features: numeric only, minus leak columns
    feature_cols = [
        c for c in df.columns
        if c not in LEAK_COLS and pd.api.types.is_numeric_dtype(df[c])
    ]
    X = df[feature_cols].fillna(0.0)
    print(f"  using {len(feature_cols)} numeric features")

    # Split (stratified — preserve churn ratio in both sets)
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    # Handle imbalance via scale_pos_weight
    spw = float((y_tr == 0).sum()) / float(max(1, (y_tr == 1).sum()))

    model = xgb.XGBClassifier(
        n_estimators=300, max_depth=5, learning_rate=0.05,
        subsample=0.9, colsample_bytree=0.9,
        scale_pos_weight=spw, eval_metric="auc",
        random_state=42,
    )
    print("\nTraining XGBoost ...")
    model.fit(X_tr, y_tr)

    # Evaluate on held-out test set
    proba = model.predict_proba(X_te)[:, 1]
    pred = (proba >= 0.5).astype(int)

    print("\n" + "=" * 55)
    print("HONEST METRICS (held-out 25% test set)")
    print("=" * 55)
    print(f"  AUC:        {roc_auc_score(y_te, proba):.3f}   (1.0=perfect, 0.5=coin flip)")
    print(f"  Precision:  {precision_score(y_te, pred):.3f}   (of flagged, how many truly churn)")
    print(f"  Recall:     {recall_score(y_te, pred):.3f}   (of churners, how many we catch)")
    print(f"  F1:         {f1_score(y_te, pred):.3f}")
    cm = confusion_matrix(y_te, pred)
    print(f"\n  Confusion matrix:")
    print(f"               pred_stay  pred_churn")
    print(f"  true_stay      {cm[0,0]:5d}      {cm[0,1]:5d}")
    print(f"  true_churn     {cm[1,0]:5d}      {cm[1,1]:5d}")

    # Feature importance — LEAK DETECTOR
    print("\n" + "=" * 55)
    print("TOP 12 FEATURES (leak check: is any one >60%?)")
    print("=" * 55)
    imp = pd.Series(model.feature_importances_, index=feature_cols).sort_values(ascending=False)
    for name, val in imp.head(12).items():
        bar = "#" * int(val * 50)
        print(f"  {name:28s} {val:6.1%}  {bar}")
    top1 = imp.iloc[0]; top3 = imp.head(3).sum()
    if top1 > 0.50 or top3 > 0.75:
        print(f"\n  WARNING: top1={top1:.0%}, top3={top3:.0%} — possible LEAK.")
    else:
        print(f"\n  OK: top1={top1:.0%}, top3={top3:.0%} — signal spread out.")
    if roc_auc_score(y_te, proba) > 0.995:
        print("  WARNING: AUC ~1.0 is almost always leakage, not skill.")

    # Save
    with open(f"{OUT_DIR}/churn_model.pkl", "wb") as f:
        pickle.dump({"model": model, "features": feature_cols}, f)
    print(f"\nSaved model -> {OUT_DIR}/churn_model.pkl ({len(feature_cols)} features)")

if __name__ == "__main__":
    main()

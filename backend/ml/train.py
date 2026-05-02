"""Eğitim pipeline'ı.

Aşamalar:
1. DB'den v_employee_overview tablosunu çek
2. Train/test split
3. ColumnTransformer (numeric scaling + one-hot encoding)
4. 3 model dene (LogReg, RandomForest, XGBoost) -> en iyi ROC-AUC kazanır
5. Joblib ile diske yaz, model_registry tablosuna kaydet, aktif olarak işaretle

Kullanım:
    python -m ml.train
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sqlalchemy import text
from xgboost import XGBClassifier

from app.core.config import settings
from app.db.session import SessionLocal, engine
from ml.features import CATEGORICAL_FEATURES, NUMERIC_FEATURES

MODEL_DIR = Path(settings.ML_MODEL_DIR)
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def load_data() -> pd.DataFrame:
    sql = """
        SELECT
            e.age, e.gender, e.marital_status, e.education, e.education_field,
            d.name AS department, jr.title AS job_role, e.business_travel,
            e.distance_from_home, e.years_at_company, e.years_in_current_role,
            e.years_since_last_promotion, e.years_with_curr_manager,
            e.total_working_years, e.num_companies_worked,
            e.overtime,  -- bool olarak gelir; to_dataframe Yes/No'ya çevirir
            em.monthly_income, em.percent_salary_hike, em.stock_option_level,
            em.job_satisfaction, em.environment_satisfaction, em.relationship_satisfaction,
            em.work_life_balance, em.job_involvement, em.performance_rating,
            em.training_times_last_year,
            CASE WHEN e.attrition THEN 1 ELSE 0 END AS y
        FROM employees e
        JOIN departments d ON d.id = e.department_id
        JOIN job_roles  jr ON jr.id = e.job_role_id
        LEFT JOIN LATERAL (
            SELECT * FROM employee_metrics m
             WHERE m.employee_id = e.id
             ORDER BY m.snapshot_date DESC LIMIT 1
        ) em ON TRUE
    """
    return pd.read_sql(sql, engine)


def build_pipeline(model) -> Pipeline:
    pre = ColumnTransformer([
        ("num", StandardScaler(), NUMERIC_FEATURES),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
    ])
    return Pipeline([("pre", pre), ("clf", model)])


def evaluate(y_true, y_pred, y_prob) -> dict:
    return {
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "precision": round(precision_score(y_true, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_true, y_pred, zero_division=0), 4),
        "f1": round(f1_score(y_true, y_pred, zero_division=0), 4),
        "roc_auc": round(roc_auc_score(y_true, y_prob), 4),
    }


def train_all(df: pd.DataFrame) -> tuple[str, Pipeline, dict]:
    X = df.drop(columns=["y"])
    y = df["y"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    candidates = {
        "logistic_regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "random_forest": RandomForestClassifier(n_estimators=300, class_weight="balanced", random_state=42, n_jobs=-1),
        "xgboost": XGBClassifier(
            n_estimators=400, max_depth=4, learning_rate=0.05,
            subsample=0.9, colsample_bytree=0.9,
            eval_metric="logloss", random_state=42, n_jobs=-1,
        ),
    }

    best_name, best_pipe, best_metrics = None, None, None
    for name, model in candidates.items():
        pipe = build_pipeline(model)
        pipe.fit(Xtr, ytr)
        prob = pipe.predict_proba(Xte)[:, 1]
        pred = (prob >= 0.5).astype(int)
        m = evaluate(yte, pred, prob)
        print(f"   {name:22s} | AUC={m['roc_auc']:.4f}  F1={m['f1']:.4f}  Acc={m['accuracy']:.4f}")
        if best_metrics is None or m["roc_auc"] > best_metrics["roc_auc"]:
            best_name, best_pipe, best_metrics = name, pipe, m
    return best_name, best_pipe, best_metrics


def register_model(version: str, algorithm: str, metrics: dict, file_path: str, features: list[str]) -> None:
    db = SessionLocal()
    try:
        # Eski aktif modeli pasifleştir
        db.execute(text("UPDATE model_registry SET is_active = FALSE WHERE is_active = TRUE"))
        db.execute(
            text("""
                INSERT INTO model_registry (version, algorithm, metrics, feature_list, file_path, is_active)
                VALUES (:v, :a, CAST(:m AS jsonb), CAST(:f AS jsonb), :p, TRUE)
            """),
            {"v": version, "a": algorithm, "m": json.dumps(metrics),
             "f": json.dumps(features), "p": file_path},
        )
        db.commit()
    finally:
        db.close()


def main() -> None:
    print("-> Veri DB'den çekiliyor ...")
    df = load_data()
    print(f"   Satır sayısı: {len(df)} | pozitif oran: {df['y'].mean():.3f}")

    print("-> Modeller eğitiliyor ...")
    name, pipe, metrics = train_all(df)
    version = f"v_{datetime.now():%Y%m%d_%H%M%S}_{name}"
    file_path = str(MODEL_DIR / f"{version}.joblib")
    joblib.dump(pipe, file_path)
    register_model(version, name, metrics, file_path, NUMERIC_FEATURES + CATEGORICAL_FEATURES)
    print(f"OK: En iyi model = {name} | metrikler = {metrics}")
    print(f"   kayıt: {file_path}")


if __name__ == "__main__":
    main()

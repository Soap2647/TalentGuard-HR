"""Tahmin servisi — aktif modeli yükler, tek satır için olasılık + SHAP döner."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import shap
from sqlalchemy import text

from app.db.session import SessionLocal
from ml.features import ALL_FEATURES, to_dataframe


@lru_cache(maxsize=4)
def _load_active() -> tuple[Any, str, int]:
    """(pipeline, version, model_id) döner."""
    db = SessionLocal()
    try:
        row = db.execute(
            text("SELECT id, version, file_path FROM model_registry WHERE is_active LIMIT 1")
        ).first()
    finally:
        db.close()
    if not row:
        raise RuntimeError("Aktif model bulunamadı. Önce `python -m ml.train` çalıştırın.")
    pipe = joblib.load(row.file_path)
    return pipe, row.version, row.id


def reset_cache() -> None:
    _load_active.cache_clear()


def risk_level(prob: float) -> str:
    if prob >= 0.70:
        return "high"
    if prob >= 0.40:
        return "medium"
    return "low"


def predict_one(features: dict) -> dict:
    pipe, version, model_id = _load_active()
    df = to_dataframe([features])
    prob = float(pipe.predict_proba(df)[0, 1])
    shap_top = _explain(pipe, df, top_k=5)
    return {
        "churn_prob": round(prob, 4),
        "risk_level": risk_level(prob),
        "model_version": version,
        "model_id": model_id,
        "shap_values": shap_top,
    }


def _explain(pipe, df: pd.DataFrame, top_k: int = 5) -> dict:
    """Top-K katkı sağlayan feature ve SHAP değeri."""
    try:
        pre = pipe.named_steps["pre"]
        clf = pipe.named_steps["clf"]
        X_trans = pre.transform(df)
        if hasattr(X_trans, "toarray"):
            X_trans = X_trans.toarray()

        # Tree-based modeller için TreeExplainer (XGBoost / RandomForest)
        try:
            explainer = shap.TreeExplainer(clf)
            sv = explainer.shap_values(X_trans)
        except Exception:
            explainer = shap.LinearExplainer(clf, X_trans)
            sv = explainer.shap_values(X_trans)

        if isinstance(sv, list):
            sv = sv[1] if len(sv) > 1 else sv[0]
        sv = np.asarray(sv)[0]

        feat_names = pre.get_feature_names_out()
        idx = np.argsort(np.abs(sv))[::-1][:top_k]
        return {
            "top_features": [
                {"feature": str(feat_names[i]), "shap": round(float(sv[i]), 4)}
                for i in idx
            ]
        }
    except Exception as e:  # noqa: BLE001
        return {"error": f"SHAP açıklaması üretilemedi: {e}"}

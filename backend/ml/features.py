"""Feature engineering — DB satırından modele girecek vektörü üretir."""
from __future__ import annotations

from typing import Any

import pandas as pd

NUMERIC_FEATURES = [
    "age",
    "distance_from_home",
    "years_at_company",
    "years_in_current_role",
    "years_since_last_promotion",
    "years_with_curr_manager",
    "total_working_years",
    "num_companies_worked",
    "monthly_income",
    "percent_salary_hike",
    "stock_option_level",
    "job_satisfaction",
    "environment_satisfaction",
    "relationship_satisfaction",
    "work_life_balance",
    "job_involvement",
    "performance_rating",
    "training_times_last_year",
    "education",
]
CATEGORICAL_FEATURES = [
    "gender",
    "marital_status",
    "education_field",
    "department",
    "job_role",
    "business_travel",
    "overtime",
]
ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def to_dataframe(rows: list[dict[str, Any]]) -> pd.DataFrame:
    """Liste/dict girdisini standart DataFrame'e çevirir."""
    df = pd.DataFrame(rows)
    for c in ALL_FEATURES:
        if c not in df.columns:
            df[c] = None
    # Eğitim SQL'i "Yes"/"No" üretir; bool veya "True"/"False" gelirse normalize et
    def _ot_normalize(v: Any) -> str:
        if isinstance(v, bool):
            return "Yes" if v else "No"
        if isinstance(v, str) and v.lower() in ("true", "1"):
            return "Yes"
        if isinstance(v, str) and v.lower() in ("false", "0"):
            return "No"
        return str(v)

    df["overtime"] = df["overtime"].apply(_ot_normalize)
    return df[ALL_FEATURES]

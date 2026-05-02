from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel


class PredictRequest(BaseModel):
    """Adhoc tahmin isteği — frontend formundan gelir."""
    age: int
    gender: str
    marital_status: str
    education: int
    education_field: str
    department: str
    job_role: str
    business_travel: str
    distance_from_home: int
    years_at_company: int
    years_in_current_role: int
    years_since_last_promotion: int
    years_with_curr_manager: int
    total_working_years: int
    num_companies_worked: int
    monthly_income: float
    percent_salary_hike: float
    stock_option_level: int
    job_satisfaction: int
    environment_satisfaction: int
    relationship_satisfaction: int
    work_life_balance: int
    job_involvement: int
    performance_rating: int
    training_times_last_year: int
    overtime: bool


class PredictResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    churn_prob: float
    risk_level: str
    model_version: str
    shap_values: dict


class PredictionRecord(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    employee_id: int
    churn_prob: Decimal
    risk_level: str
    shap_values: dict | None
    created_at: datetime

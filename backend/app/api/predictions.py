import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.db.session import get_db
from app.models import Employee, User
from app.schemas.prediction import PredictRequest, PredictResponse
from ml.predict import predict_one

router = APIRouter(prefix="/api/predictions", tags=["predictions"])


@router.post("/adhoc", response_model=PredictResponse)
def predict_adhoc(req: PredictRequest, _: User = Depends(get_current_user)):
    """Form ile gelen tek bir senaryo için hızlı tahmin."""
    try:
        return predict_one(req.model_dump())
    except RuntimeError as e:
        raise HTTPException(503, str(e))


@router.post("/employee/{emp_id}")
def predict_for_employee(
    emp_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Bir çalışanın güncel verisiyle tahmin yapar ve `predictions` tablosuna yazar."""
    row = db.execute(
        text("""
            SELECT
                e.age, e.gender, e.marital_status, e.education, e.education_field,
                d.name AS department, jr.title AS job_role, e.business_travel,
                e.distance_from_home, e.years_at_company, e.years_in_current_role,
                e.years_since_last_promotion, e.years_with_curr_manager,
                e.total_working_years, e.num_companies_worked, e.overtime,
                em.monthly_income, em.percent_salary_hike, em.stock_option_level,
                em.job_satisfaction, em.environment_satisfaction, em.relationship_satisfaction,
                em.work_life_balance, em.job_involvement, em.performance_rating,
                em.training_times_last_year, e.department_id
            FROM employees e
            JOIN departments d ON d.id = e.department_id
            JOIN job_roles  jr ON jr.id = e.job_role_id
            LEFT JOIN LATERAL (
                SELECT * FROM employee_metrics m
                 WHERE m.employee_id = e.id
                 ORDER BY m.snapshot_date DESC LIMIT 1
            ) em ON TRUE
            WHERE e.id = :eid
        """),
        {"eid": emp_id},
    ).mappings().first()
    if not row:
        raise HTTPException(404, "Çalışan veya metrik bulunamadı")
    if user.role == "manager" and user.department_id and row["department_id"] != user.department_id:
        raise HTTPException(403, "Yetki yok")

    features = dict(row)
    features.pop("department_id", None)
    try:
        result = predict_one(features)
    except RuntimeError as e:
        raise HTTPException(503, str(e))

    db.execute(
        text("""
            INSERT INTO predictions (employee_id, model_id, churn_prob, risk_level, shap_values, created_by)
            VALUES (:e, :m, :p, :r, CAST(:s AS jsonb), :u)
        """),
        {
            "e": emp_id, "m": result["model_id"],
            "p": result["churn_prob"], "r": result["risk_level"],
            "s": json.dumps(result["shap_values"]), "u": user.id,
        },
    )
    db.commit()
    return result


@router.post("/batch")
def batch_predict(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "hr")),
):
    """Tüm çalışanlar için tahmin üretir (batch)."""
    ids = [r[0] for r in db.execute(text("SELECT id FROM employees ORDER BY id")).all()]
    ok, fail = 0, 0
    for eid in ids:
        try:
            predict_for_employee(eid, db, user)  # type: ignore[arg-type]
            ok += 1
        except Exception:
            fail += 1
    return {"processed": ok, "failed": fail, "total": len(ids)}

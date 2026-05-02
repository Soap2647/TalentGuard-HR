from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models import User

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/kpis")
def kpis(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    row = db.execute(text("SELECT * FROM fn_dashboard_kpis()")).mappings().first()
    return dict(row) if row else {}


@router.get("/department-attrition")
def department_attrition(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = db.execute(text("SELECT * FROM v_department_attrition_rate")).mappings().all()
    return [dict(r) for r in rows]


@router.get("/monthly-predictions")
def monthly_predictions(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = db.execute(text("SELECT * FROM v_monthly_predictions LIMIT 12")).mappings().all()
    return [dict(r) for r in rows]


@router.get("/high-risk")
def high_risk(db: Session = Depends(get_db), _: User = Depends(get_current_user), limit: int = 20):
    rows = db.execute(
        text("SELECT * FROM v_high_risk_employees LIMIT :l"), {"l": limit}
    ).mappings().all()
    return [dict(r) for r in rows]


@router.get("/risk-distribution")
def risk_distribution(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = db.execute(
        text("""
            SELECT latest_risk_level AS risk, COUNT(*) AS count
            FROM v_employee_overview
            WHERE latest_risk_level IS NOT NULL
            GROUP BY latest_risk_level
        """)
    ).mappings().all()
    return [dict(r) for r in rows]

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.db.session import get_db
from app.models import Employee, EmployeeMetric, User
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeOut,
    EmployeeUpdate,
    MetricCreate,
)

router = APIRouter(prefix="/api/employees", tags=["employees"])


@router.get("")
def list_employees(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    q: str | None = Query(None, description="İsim veya e-posta arama"),
    department_id: int | None = None,
    risk: str | None = Query(None, pattern="^(low|medium|high)$"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """v_employee_overview view'ından sayfalı listeleme."""
    where, params = [], {"limit": limit, "offset": offset}
    if q:
        where.append("(LOWER(full_name) LIKE :q OR LOWER(email) LIKE :q)")
        params["q"] = f"%{q.lower()}%"
    if department_id:
        where.append("department_id = :dep")
        params["dep"] = department_id
    if risk:
        where.append("latest_risk_level = :risk")
        params["risk"] = risk

    # Manager kendi departmanına kilitli (row-level filter)
    if user.role == "manager" and user.department_id:
        where.append("department_id = :user_dep")
        params["user_dep"] = user.department_id

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    rows = db.execute(
        text(f"""
            SELECT * FROM v_employee_overview
            {where_sql}
            ORDER BY id
            LIMIT :limit OFFSET :offset
        """),
        params,
    ).mappings().all()
    total = db.execute(
        text(f"SELECT COUNT(*) FROM v_employee_overview {where_sql}"), params
    ).scalar()
    return {"total": total, "items": [dict(r) for r in rows]}


@router.get("/{emp_id}")
def get_employee(emp_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(404, "Çalışan bulunamadı")
    if user.role == "manager" and user.department_id and emp.department_id != user.department_id:
        raise HTTPException(403, "Yetki yok")

    latest_metric = (
        db.query(EmployeeMetric)
        .filter(EmployeeMetric.employee_id == emp_id)
        .order_by(EmployeeMetric.snapshot_date.desc())
        .first()
    )
    history = db.execute(
        text("SELECT * FROM fn_employee_risk_history(:eid)"), {"eid": emp_id}
    ).mappings().all()

    return {
        "employee": EmployeeOut.model_validate(emp).model_dump(mode="json"),
        "metric": latest_metric.__dict__ if latest_metric else None,
        "department": emp.department.name,
        "job_role": emp.job_role.title,
        "risk_history": [dict(r) for r in history],
    }


@router.post("", response_model=EmployeeOut, status_code=201)
def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "hr")),
):
    if db.query(Employee).filter(Employee.employee_number == payload.employee_number).first():
        raise HTTPException(400, "Bu employee_number zaten kayıtlı")
    emp = Employee(**payload.model_dump())
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


@router.patch("/{emp_id}", response_model=EmployeeOut)
def update_employee(
    emp_id: int,
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "hr")),
):
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(404, "Çalışan bulunamadı")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(emp, k, v)
    db.commit()
    db.refresh(emp)
    return emp


@router.delete("/{emp_id}", status_code=204)
def delete_employee(
    emp_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(404, "Çalışan bulunamadı")
    db.delete(emp)
    db.commit()


@router.post("/{emp_id}/metrics", status_code=201)
def add_metric(
    emp_id: int,
    payload: MetricCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "hr")),
):
    if not db.query(Employee).filter(Employee.id == emp_id).first():
        raise HTTPException(404, "Çalışan bulunamadı")
    m = EmployeeMetric(employee_id=emp_id, **payload.model_dump())
    db.add(m)
    db.commit()
    return {"ok": True}


@router.get("/-/lookups/departments")
def list_departments(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = db.execute(text("SELECT id, name FROM departments ORDER BY name")).mappings().all()
    return [dict(r) for r in rows]


@router.get("/-/lookups/job_roles")
def list_job_roles(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = db.execute(text("SELECT id, title FROM job_roles ORDER BY title")).mappings().all()
    return [dict(r) for r in rows]

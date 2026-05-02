from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.core.security import hash_password
from app.db.session import get_db
from app.models import User
from app.schemas.auth import UserCreate, UserOut

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ----- Users -----
@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    return db.query(User).order_by(User.id).all()


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(400, "Bu kullanıcı adı kayıtlı")
    if payload.role not in ("admin", "hr", "manager"):
        raise HTTPException(400, "Geçersiz rol")
    u = User(
        username=payload.username, full_name=payload.full_name, email=payload.email,
        password_hash=hash_password(payload.password), role=payload.role,
        department_id=payload.department_id,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@router.delete("/users/{uid}", status_code=204)
def delete_user(uid: int, db: Session = Depends(get_db), me: User = Depends(require_role("admin"))):
    if uid == me.id:
        raise HTTPException(400, "Kendinizi silemezsiniz")
    u = db.query(User).filter(User.id == uid).first()
    if not u:
        raise HTTPException(404, "Kullanıcı yok")
    db.delete(u)
    db.commit()


# ----- Audit log -----
@router.get("/audit-log")
def audit_log(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
    table: str | None = None,
    limit: int = Query(100, le=500),
    offset: int = 0,
):
    where, params = [], {"l": limit, "o": offset}
    if table:
        where.append("table_name = :t")
        params["t"] = table
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    rows = db.execute(
        text(f"""
            SELECT id, table_name, record_id, operation, changed_by, changed_at,
                   old_data, new_data
              FROM audit_log {where_sql}
             ORDER BY changed_at DESC LIMIT :l OFFSET :o
        """),
        params,
    ).mappings().all()
    return [dict(r) for r in rows]


# ----- Models -----
@router.get("/models")
def list_models(db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    rows = db.execute(
        text("""
            SELECT id, version, algorithm, metrics, is_active, trained_at
              FROM model_registry ORDER BY trained_at DESC
        """)
    ).mappings().all()
    return [dict(r) for r in rows]


@router.post("/models/{model_id}/activate")
def activate_model(model_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("admin"))):
    db.execute(text("UPDATE model_registry SET is_active = FALSE WHERE is_active = TRUE"))
    res = db.execute(
        text("UPDATE model_registry SET is_active = TRUE WHERE id = :i RETURNING version"),
        {"i": model_id},
    ).first()
    db.commit()
    if not res:
        raise HTTPException(404, "Model bulunamadı")
    # cache temizle
    from ml.predict import reset_cache
    reset_cache()
    return {"activated": res[0]}


@router.post("/models/retrain")
def retrain(_: User = Depends(require_role("admin"))):
    """Yeni eğitim turunu tetikler (sync; küçük dataset için yeterli)."""
    from ml.train import main as train_main
    train_main()
    from ml.predict import reset_cache
    reset_cache()
    return {"status": "ok"}

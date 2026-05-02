from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def set_audit_user(db: Session, username: str) -> None:
    """PostgreSQL session var'ını set eder — audit trigger bunu okuyacak."""
    db.execute(text("SELECT set_config('app.current_user', :u, false)"), {"u": username})

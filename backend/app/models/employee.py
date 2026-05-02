from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import String, Integer, Boolean, Date, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str | None] = mapped_column(String(150), unique=True)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    marital_status: Mapped[str | None] = mapped_column(String(20))
    education: Mapped[int | None] = mapped_column(Integer)
    education_field: Mapped[str | None] = mapped_column(String(50))
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=False)
    job_role_id: Mapped[int] = mapped_column(ForeignKey("job_roles.id"), nullable=False)
    business_travel: Mapped[str | None] = mapped_column(String(30))
    distance_from_home: Mapped[int | None] = mapped_column(Integer)
    hire_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    years_at_company: Mapped[int] = mapped_column(Integer, nullable=False)
    years_in_current_role: Mapped[int | None] = mapped_column(Integer)
    years_since_last_promotion: Mapped[int | None] = mapped_column(Integer)
    years_with_curr_manager: Mapped[int | None] = mapped_column(Integer)
    total_working_years: Mapped[int | None] = mapped_column(Integer)
    num_companies_worked: Mapped[int | None] = mapped_column(Integer)
    overtime: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    attrition: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    department = relationship("Department", lazy="joined")
    job_role = relationship("JobRole", lazy="joined")
    metrics = relationship("EmployeeMetric", back_populates="employee", cascade="all, delete-orphan")


class EmployeeMetric(Base):
    __tablename__ = "employee_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    snapshot_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    monthly_income: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    percent_salary_hike: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    stock_option_level: Mapped[int | None] = mapped_column(Integer)
    job_satisfaction: Mapped[int | None] = mapped_column(Integer)
    environment_satisfaction: Mapped[int | None] = mapped_column(Integer)
    relationship_satisfaction: Mapped[int | None] = mapped_column(Integer)
    work_life_balance: Mapped[int | None] = mapped_column(Integer)
    job_involvement: Mapped[int | None] = mapped_column(Integer)
    performance_rating: Mapped[int | None] = mapped_column(Integer)
    training_times_last_year: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    employee = relationship("Employee", back_populates="metrics")

from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, EmailStr


class EmployeeBase(BaseModel):
    employee_number: int
    first_name: str
    last_name: str
    email: EmailStr | None = None
    age: int
    gender: str
    marital_status: str | None = None
    education: int | None = None
    education_field: str | None = None
    department_id: int
    job_role_id: int
    business_travel: str | None = None
    distance_from_home: int | None = None
    hire_date: date
    years_at_company: int
    years_in_current_role: int | None = None
    years_since_last_promotion: int | None = None
    years_with_curr_manager: int | None = None
    total_working_years: int | None = None
    num_companies_worked: int | None = None
    overtime: bool = False
    attrition: bool = False


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    age: int | None = None
    department_id: int | None = None
    job_role_id: int | None = None
    overtime: bool | None = None
    attrition: bool | None = None


class EmployeeOut(EmployeeBase):
    model_config = {"from_attributes": True}

    id: int
    created_at: datetime


class EmployeeOverview(BaseModel):
    id: int
    employee_number: int
    full_name: str
    email: str | None
    age: int
    gender: str
    department: str
    job_role: str
    years_at_company: int
    overtime: bool
    attrition: bool
    monthly_income: Decimal | None = None
    job_satisfaction: int | None = None
    work_life_balance: int | None = None
    performance_rating: int | None = None
    latest_churn_prob: Decimal | None = None
    latest_risk_level: str | None = None


class MetricCreate(BaseModel):
    monthly_income: Decimal
    percent_salary_hike: Decimal | None = None
    stock_option_level: int | None = None
    job_satisfaction: int | None = None
    environment_satisfaction: int | None = None
    relationship_satisfaction: int | None = None
    work_life_balance: int | None = None
    job_involvement: int | None = None
    performance_rating: int | None = None
    training_times_last_year: int | None = None

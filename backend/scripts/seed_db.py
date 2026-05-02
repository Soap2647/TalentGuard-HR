"""IBM HR Analytics CSV dosyasını PostgreSQL'e yükler.

Dataset: WA_Fn-UseC_-HR-Employee-Attrition.csv (Kaggle)
- data/ klasörüne indirilmeli
- Veya bu script otomatik üretebilir (sentetik fallback)

Kullanım:
    python -m scripts.seed_db
"""
from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker  # opsiyonel; yoksa email rastgele üretilir
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import SessionLocal, set_audit_user

DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "ibm_hr_attrition.csv"

# IBM HR dataset'in raw CSV URL'i (yedek)
DATASET_URL = (
    "https://raw.githubusercontent.com/IBM/employee-attrition-aif360/master/"
    "data/emp_attrition.csv"
)


def load_dataframe() -> pd.DataFrame:
    if DATA_PATH.exists():
        print(f"-> CSV bulundu: {DATA_PATH}")
        return pd.read_csv(DATA_PATH)
    print(f"-> CSV bulunamadı, dataset indiriliyor: {DATASET_URL}")
    df = pd.read_csv(DATASET_URL)
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA_PATH, index=False)
    return df


def seed_users(db: Session) -> None:
    print("-> Kullanıcılar yükleniyor (admin, hr, manager) ...")
    users = [
        ("admin",   "Admin User",      "admin@example.com",   "admin123",   "admin",   None),
        ("hr_user", "HR Specialist",   "hr@example.com",      "hr123",      "hr",      None),
        ("manager", "Sales Manager",   "manager@example.com", "manager123", "manager", 1),
    ]
    for username, full_name, email, pwd, role, dept in users:
        db.execute(
            text("""
                INSERT INTO users (username, full_name, email, password_hash, role, department_id)
                VALUES (:u, :f, :e, :p, :r, :d)
                ON CONFLICT (username) DO NOTHING
            """),
            {"u": username, "f": full_name, "e": email, "p": hash_password(pwd), "r": role, "d": dept},
        )


def seed_organization(db: Session, df: pd.DataFrame) -> tuple[dict, dict]:
    print("-> Departmanlar ve pozisyonlar yükleniyor ...")
    dept_map: dict[str, int] = {}
    for d in df["Department"].dropna().unique():
        row = db.execute(
            text("INSERT INTO departments (name) VALUES (:n) ON CONFLICT (name) DO UPDATE SET name=EXCLUDED.name RETURNING id"),
            {"n": d},
        ).first()
        dept_map[d] = row[0]

    role_map: dict[str, int] = {}
    for r in df["JobRole"].dropna().unique():
        row = db.execute(
            text("INSERT INTO job_roles (title, job_level) VALUES (:t, 1) ON CONFLICT (title) DO UPDATE SET title=EXCLUDED.title RETURNING id"),
            {"t": r},
        ).first()
        role_map[r] = row[0]
    return dept_map, role_map


def seed_employees(db: Session, df: pd.DataFrame, dept_map: dict, role_map: dict) -> None:
    print(f"-> {len(df)} çalışan kaydı yükleniyor ...")
    fake = Faker()
    Faker.seed(42)
    random.seed(42)

    today = date.today()
    for _, r in df.iterrows():
        years_at = int(r["YearsAtCompany"])
        hire = today - timedelta(days=years_at * 365 + random.randint(0, 364))
        first = fake.first_name_male() if r["Gender"] == "Male" else fake.first_name_female()
        last = fake.last_name()
        email = f"{first.lower()}.{last.lower()}.{int(r['EmployeeNumber'])}@company.example"

        emp_id = db.execute(
            text("""
                INSERT INTO employees (
                    employee_number, first_name, last_name, email,
                    age, gender, marital_status, education, education_field,
                    department_id, job_role_id, business_travel, distance_from_home,
                    hire_date, years_at_company, years_in_current_role,
                    years_since_last_promotion, years_with_curr_manager,
                    total_working_years, num_companies_worked, overtime, attrition
                ) VALUES (
                    :emp_no, :fn, :ln, :em,
                    :age, :gen, :ms, :edu, :ef,
                    :dep, :jr, :bt, :dfh,
                    :hd, :yac, :yicr, :yslp, :ywcm, :twy, :ncw, :ot, :att
                )
                ON CONFLICT (employee_number) DO NOTHING
                RETURNING id
            """),
            {
                "emp_no": int(r["EmployeeNumber"]),
                "fn": first, "ln": last, "em": email,
                "age": int(r["Age"]), "gen": r["Gender"],
                "ms": r["MaritalStatus"], "edu": int(r["Education"]),
                "ef": r["EducationField"],
                "dep": dept_map[r["Department"]],
                "jr": role_map[r["JobRole"]],
                "bt": r["BusinessTravel"], "dfh": int(r["DistanceFromHome"]),
                "hd": hire, "yac": years_at,
                "yicr": int(r["YearsInCurrentRole"]),
                "yslp": int(r["YearsSinceLastPromotion"]),
                "ywcm": int(r["YearsWithCurrManager"]),
                "twy": int(r["TotalWorkingYears"]),
                "ncw": int(r["NumCompaniesWorked"]),
                "ot": r["OverTime"] == "Yes",
                "att": r["Attrition"] == "Yes",
            },
        ).first()
        if not emp_id:
            continue

        db.execute(
            text("""
                INSERT INTO employee_metrics (
                    employee_id, monthly_income, percent_salary_hike, stock_option_level,
                    job_satisfaction, environment_satisfaction, relationship_satisfaction,
                    work_life_balance, job_involvement, performance_rating, training_times_last_year
                ) VALUES (
                    :eid, :mi, :psh, :sol, :js, :es, :rs, :wlb, :ji, :pr, :ttly
                )
            """),
            {
                "eid": emp_id[0],
                "mi": float(r["MonthlyIncome"]),
                "psh": float(r["PercentSalaryHike"]),
                "sol": int(r["StockOptionLevel"]),
                "js": int(r["JobSatisfaction"]),
                "es": int(r["EnvironmentSatisfaction"]),
                "rs": int(r["RelationshipSatisfaction"]),
                "wlb": int(r["WorkLifeBalance"]),
                "ji": int(r["JobInvolvement"]),
                "pr": int(r["PerformanceRating"]),
                "ttly": int(r["TrainingTimesLastYear"]),
            },
        )


def main() -> None:
    df = load_dataframe()
    db = SessionLocal()
    try:
        set_audit_user(db, "seed_script")
        dept_map, role_map = seed_organization(db, df)
        db.commit()
        seed_users(db)
        db.commit()
        seed_employees(db, df, dept_map, role_map)
        db.commit()
        print("OK: Seed tamamlandı.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

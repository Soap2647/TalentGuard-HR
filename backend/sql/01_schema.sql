-- =====================================================================
-- Çalışan Churn Tahmin Sistemi — Veritabanı Şeması
-- Veri Tabanı Yönetim Sistemleri Final Projesi
-- =====================================================================

-- Temiz başlangıç (geliştirme için)
DROP TABLE IF EXISTS audit_log CASCADE;
DROP TABLE IF EXISTS predictions CASCADE;
DROP TABLE IF EXISTS employee_metrics CASCADE;
DROP TABLE IF EXISTS employees CASCADE;
DROP TABLE IF EXISTS job_roles CASCADE;
DROP TABLE IF EXISTS departments CASCADE;
DROP TABLE IF EXISTS model_registry CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- =====================================================================
-- 1. KULLANICI YÖNETİMİ
-- =====================================================================
CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    full_name     VARCHAR(100) NOT NULL,
    email         VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role          VARCHAR(20)  NOT NULL CHECK (role IN ('admin', 'hr', 'manager')),
    department_id INTEGER,             -- manager rolü için
    is_active     BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_role ON users(role);

-- =====================================================================
-- 2. DEPARTMAN & POZİSYON (Master tablolar)
-- =====================================================================
CREATE TABLE departments (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE job_roles (
    id           SERIAL PRIMARY KEY,
    title        VARCHAR(100) NOT NULL UNIQUE,
    job_level    INTEGER      NOT NULL CHECK (job_level BETWEEN 1 AND 5),
    description  TEXT
);

-- users.department_id artık FK olarak set edilebilir
ALTER TABLE users
    ADD CONSTRAINT fk_users_department
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL;

-- =====================================================================
-- 3. ÇALIŞANLAR (Ana iş tablosu)
-- =====================================================================
CREATE TABLE employees (
    id                        SERIAL PRIMARY KEY,
    employee_number           INTEGER NOT NULL UNIQUE,
    first_name                VARCHAR(50)  NOT NULL,
    last_name                 VARCHAR(50)  NOT NULL,
    email                     VARCHAR(150) UNIQUE,
    age                       INTEGER NOT NULL CHECK (age BETWEEN 18 AND 70),
    gender                    VARCHAR(10)  NOT NULL CHECK (gender IN ('Male', 'Female', 'Other')),
    marital_status            VARCHAR(20)  CHECK (marital_status IN ('Single', 'Married', 'Divorced')),
    education                 INTEGER CHECK (education BETWEEN 1 AND 5),
    education_field           VARCHAR(50),
    department_id             INTEGER NOT NULL REFERENCES departments(id) ON DELETE RESTRICT,
    job_role_id               INTEGER NOT NULL REFERENCES job_roles(id) ON DELETE RESTRICT,
    business_travel           VARCHAR(30) CHECK (business_travel IN ('Non-Travel', 'Travel_Rarely', 'Travel_Frequently')),
    distance_from_home        INTEGER CHECK (distance_from_home >= 0),
    hire_date                 DATE NOT NULL DEFAULT CURRENT_DATE,
    years_at_company          INTEGER NOT NULL CHECK (years_at_company >= 0),
    years_in_current_role     INTEGER CHECK (years_in_current_role >= 0),
    years_since_last_promotion INTEGER CHECK (years_since_last_promotion >= 0),
    years_with_curr_manager   INTEGER CHECK (years_with_curr_manager >= 0),
    total_working_years       INTEGER CHECK (total_working_years >= 0),
    num_companies_worked      INTEGER CHECK (num_companies_worked >= 0),
    overtime                  BOOLEAN NOT NULL DEFAULT FALSE,
    attrition                 BOOLEAN NOT NULL DEFAULT FALSE,  -- Geçmiş etiket (training)
    created_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_employees_department  ON employees(department_id);
CREATE INDEX idx_employees_job_role    ON employees(job_role_id);
CREATE INDEX idx_employees_attrition   ON employees(attrition);

-- =====================================================================
-- 4. EMPLOYEE METRICS (Zaman serili performans/maaş)
-- =====================================================================
CREATE TABLE employee_metrics (
    id                          SERIAL PRIMARY KEY,
    employee_id                 INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    snapshot_date               DATE NOT NULL DEFAULT CURRENT_DATE,
    monthly_income              NUMERIC(10, 2) NOT NULL CHECK (monthly_income > 0),
    percent_salary_hike         NUMERIC(5, 2) CHECK (percent_salary_hike >= 0),
    stock_option_level          INTEGER CHECK (stock_option_level BETWEEN 0 AND 3),
    job_satisfaction            INTEGER CHECK (job_satisfaction BETWEEN 1 AND 4),
    environment_satisfaction    INTEGER CHECK (environment_satisfaction BETWEEN 1 AND 4),
    relationship_satisfaction   INTEGER CHECK (relationship_satisfaction BETWEEN 1 AND 4),
    work_life_balance           INTEGER CHECK (work_life_balance BETWEEN 1 AND 4),
    job_involvement             INTEGER CHECK (job_involvement BETWEEN 1 AND 4),
    performance_rating          INTEGER CHECK (performance_rating BETWEEN 1 AND 4),
    training_times_last_year    INTEGER CHECK (training_times_last_year >= 0),
    created_at                  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (employee_id, snapshot_date)
);

CREATE INDEX idx_metrics_employee ON employee_metrics(employee_id);
CREATE INDEX idx_metrics_date     ON employee_metrics(snapshot_date DESC);

-- =====================================================================
-- 5. MODEL REGISTRY
-- =====================================================================
CREATE TABLE model_registry (
    id           SERIAL PRIMARY KEY,
    version      VARCHAR(50) NOT NULL UNIQUE,
    algorithm    VARCHAR(50) NOT NULL,
    metrics      JSONB NOT NULL,             -- {accuracy, precision, recall, f1, roc_auc}
    feature_list JSONB NOT NULL,             -- ["age","monthly_income",...]
    file_path    VARCHAR(500) NOT NULL,
    is_active    BOOLEAN NOT NULL DEFAULT FALSE,
    trained_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    trained_by   INTEGER REFERENCES users(id) ON DELETE SET NULL
);

-- Aynı anda sadece 1 model aktif olabilir (partial unique index)
CREATE UNIQUE INDEX uniq_active_model ON model_registry(is_active) WHERE is_active = TRUE;

-- =====================================================================
-- 6. PREDICTIONS (ML çıktıları)
-- =====================================================================
CREATE TABLE predictions (
    id            SERIAL PRIMARY KEY,
    employee_id   INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    model_id      INTEGER NOT NULL REFERENCES model_registry(id) ON DELETE RESTRICT,
    churn_prob    NUMERIC(5, 4) NOT NULL CHECK (churn_prob BETWEEN 0 AND 1),
    risk_level    VARCHAR(10) NOT NULL CHECK (risk_level IN ('low', 'medium', 'high')),
    shap_values   JSONB,                    -- Top feature contributions
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by    INTEGER REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_predictions_employee  ON predictions(employee_id);
CREATE INDEX idx_predictions_risk      ON predictions(risk_level);
CREATE INDEX idx_predictions_created   ON predictions(created_at DESC);
-- GIN index for JSONB queries
CREATE INDEX idx_predictions_shap_gin  ON predictions USING GIN (shap_values);

-- =====================================================================
-- 7. AUDIT LOG (Trigger ile dolduralacak)
-- =====================================================================
CREATE TABLE audit_log (
    id            BIGSERIAL PRIMARY KEY,
    table_name    VARCHAR(100) NOT NULL,
    record_id     INTEGER,
    operation     VARCHAR(10) NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
    old_data      JSONB,
    new_data      JSONB,
    changed_by    VARCHAR(100),
    changed_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_table   ON audit_log(table_name);
CREATE INDEX idx_audit_changed ON audit_log(changed_at DESC);

-- =====================================================================
-- updated_at otomatik güncellemesi için generic trigger fonksiyonu
-- =====================================================================
CREATE OR REPLACE FUNCTION fn_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

CREATE TRIGGER trg_employees_updated_at
    BEFORE UPDATE ON employees
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

-- =====================================================================
-- VIEWS (Görünümler)
-- =====================================================================

-- 1) Yüksek riskli çalışanlar (en güncel tahmine göre)
CREATE OR REPLACE VIEW v_high_risk_employees AS
SELECT
    e.id              AS employee_id,
    e.employee_number,
    e.first_name || ' ' || e.last_name AS full_name,
    d.name            AS department,
    jr.title          AS job_role,
    p.churn_prob,
    p.risk_level,
    p.created_at      AS predicted_at
FROM employees e
JOIN departments d ON d.id = e.department_id
JOIN job_roles  jr ON jr.id = e.job_role_id
JOIN LATERAL (
    SELECT churn_prob, risk_level, created_at
    FROM predictions p2
    WHERE p2.employee_id = e.id
    ORDER BY p2.created_at DESC
    LIMIT 1
) p ON TRUE
WHERE p.risk_level = 'high'
ORDER BY p.churn_prob DESC;

-- 2) Departman bazlı attrition oranı
CREATE OR REPLACE VIEW v_department_attrition_rate AS
SELECT
    d.id          AS department_id,
    d.name        AS department,
    COUNT(e.id)   AS total_employees,
    SUM(CASE WHEN e.attrition THEN 1 ELSE 0 END) AS left_count,
    ROUND(
        100.0 * SUM(CASE WHEN e.attrition THEN 1 ELSE 0 END) / NULLIF(COUNT(e.id), 0),
        2
    ) AS attrition_rate_pct
FROM departments d
LEFT JOIN employees e ON e.department_id = d.id
GROUP BY d.id, d.name
ORDER BY attrition_rate_pct DESC NULLS LAST;

-- 3) Aylık tahmin trendi
CREATE OR REPLACE VIEW v_monthly_predictions AS
SELECT
    DATE_TRUNC('month', created_at)::DATE AS month,
    COUNT(*)                              AS total_predictions,
    SUM(CASE WHEN risk_level = 'high'   THEN 1 ELSE 0 END) AS high_risk,
    SUM(CASE WHEN risk_level = 'medium' THEN 1 ELSE 0 END) AS medium_risk,
    SUM(CASE WHEN risk_level = 'low'    THEN 1 ELSE 0 END) AS low_risk,
    ROUND(AVG(churn_prob)::numeric, 4)    AS avg_churn_prob
FROM predictions
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY month DESC;

-- 4) Çalışan birleşik (denormalized) görünüm — frontend listeleri için
CREATE OR REPLACE VIEW v_employee_overview AS
SELECT
    e.id,
    e.employee_number,
    e.first_name || ' ' || e.last_name AS full_name,
    e.email,
    e.age,
    e.gender,
    e.marital_status,
    d.id              AS department_id,
    d.name            AS department,
    jr.title          AS job_role,
    e.years_at_company,
    e.overtime,
    e.attrition,
    em.monthly_income,
    em.job_satisfaction,
    em.work_life_balance,
    em.performance_rating,
    p.churn_prob      AS latest_churn_prob,
    p.risk_level      AS latest_risk_level
FROM employees e
JOIN departments d ON d.id = e.department_id
JOIN job_roles  jr ON jr.id = e.job_role_id
LEFT JOIN LATERAL (
    SELECT *
    FROM employee_metrics m
    WHERE m.employee_id = e.id
    ORDER BY m.snapshot_date DESC
    LIMIT 1
) em ON TRUE
LEFT JOIN LATERAL (
    SELECT churn_prob, risk_level
    FROM predictions p2
    WHERE p2.employee_id = e.id
    ORDER BY p2.created_at DESC
    LIMIT 1
) p ON TRUE;

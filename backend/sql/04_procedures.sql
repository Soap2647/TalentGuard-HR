-- =====================================================================
-- STORED PROCEDURES & FUNCTIONS
-- =====================================================================

-- 1) Departman attrition oranı hesaplayan fonksiyon
CREATE OR REPLACE FUNCTION fn_attrition_rate_by_dept(p_dept_id INTEGER)
RETURNS NUMERIC AS $$
DECLARE
    v_rate NUMERIC;
BEGIN
    SELECT ROUND(
               100.0 * SUM(CASE WHEN attrition THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0),
               2
           )
      INTO v_rate
      FROM employees
     WHERE department_id = p_dept_id;
    RETURN COALESCE(v_rate, 0);
END;
$$ LANGUAGE plpgsql;

-- 2) Genel KPI özeti döndüren fonksiyon (dashboard için)
CREATE OR REPLACE FUNCTION fn_dashboard_kpis()
RETURNS TABLE (
    total_employees     BIGINT,
    high_risk_count     BIGINT,
    avg_tenure          NUMERIC,
    overall_attrition   NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        (SELECT COUNT(*) FROM employees)                                AS total_employees,
        (SELECT COUNT(*) FROM v_high_risk_employees)                    AS high_risk_count,
        (SELECT ROUND(AVG(years_at_company)::numeric, 2) FROM employees) AS avg_tenure,
        (SELECT ROUND(
                   100.0 * SUM(CASE WHEN attrition THEN 1 ELSE 0 END)
                   / NULLIF(COUNT(*), 0), 2)
           FROM employees)                                              AS overall_attrition;
END;
$$ LANGUAGE plpgsql;

-- 3) Risk seviyesi belirleyici (probability -> label)
CREATE OR REPLACE FUNCTION fn_risk_level(p_prob NUMERIC)
RETURNS VARCHAR AS $$
BEGIN
    IF p_prob >= 0.70 THEN
        RETURN 'high';
    ELSIF p_prob >= 0.40 THEN
        RETURN 'medium';
    ELSE
        RETURN 'low';
    END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- 4) Belirli bir çalışanın risk geçmişini döndürür
CREATE OR REPLACE FUNCTION fn_employee_risk_history(p_employee_id INTEGER)
RETURNS TABLE (
    predicted_at TIMESTAMP,
    churn_prob   NUMERIC,
    risk_level   VARCHAR,
    model_version VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT p.created_at, p.churn_prob, p.risk_level, mr.version
      FROM predictions p
      JOIN model_registry mr ON mr.id = p.model_id
     WHERE p.employee_id = p_employee_id
     ORDER BY p.created_at DESC;
END;
$$ LANGUAGE plpgsql;

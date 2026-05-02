-- =====================================================================
-- AUDIT TRIGGER'LARI
-- Tüm değişiklikleri audit_log tablosuna otomatik kaydeder
-- FastAPI middleware her request'te `app.current_user` session var'ını set eder
-- =====================================================================

CREATE OR REPLACE FUNCTION fn_audit_trigger()
RETURNS TRIGGER AS $$
DECLARE
    v_user      TEXT;
    v_old_data  JSONB;
    v_new_data  JSONB;
    v_record_id INTEGER;
BEGIN
    -- session var'dan kullanıcıyı al, yoksa 'system'
    BEGIN
        v_user := current_setting('app.current_user', TRUE);
        IF v_user IS NULL OR v_user = '' THEN
            v_user := 'system';
        END IF;
    EXCEPTION WHEN OTHERS THEN
        v_user := 'system';
    END;

    IF (TG_OP = 'DELETE') THEN
        v_old_data  := to_jsonb(OLD);
        v_new_data  := NULL;
        v_record_id := (v_old_data->>'id')::INTEGER;
    ELSIF (TG_OP = 'UPDATE') THEN
        v_old_data  := to_jsonb(OLD);
        v_new_data  := to_jsonb(NEW);
        v_record_id := (v_new_data->>'id')::INTEGER;
    ELSIF (TG_OP = 'INSERT') THEN
        v_old_data  := NULL;
        v_new_data  := to_jsonb(NEW);
        v_record_id := (v_new_data->>'id')::INTEGER;
    END IF;

    INSERT INTO audit_log (table_name, record_id, operation, old_data, new_data, changed_by)
    VALUES (TG_TABLE_NAME, v_record_id, TG_OP, v_old_data, v_new_data, v_user);

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Audit trigger'larını ilgili tablolara ekle
DROP TRIGGER IF EXISTS trg_audit_employees ON employees;
CREATE TRIGGER trg_audit_employees
    AFTER INSERT OR UPDATE OR DELETE ON employees
    FOR EACH ROW EXECUTE FUNCTION fn_audit_trigger();

DROP TRIGGER IF EXISTS trg_audit_users ON users;
CREATE TRIGGER trg_audit_users
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION fn_audit_trigger();

DROP TRIGGER IF EXISTS trg_audit_predictions ON predictions;
CREATE TRIGGER trg_audit_predictions
    AFTER INSERT OR DELETE ON predictions
    FOR EACH ROW EXECUTE FUNCTION fn_audit_trigger();

DROP TRIGGER IF EXISTS trg_audit_model_registry ON model_registry;
CREATE TRIGGER trg_audit_model_registry
    AFTER INSERT OR UPDATE OR DELETE ON model_registry
    FOR EACH ROW EXECUTE FUNCTION fn_audit_trigger();

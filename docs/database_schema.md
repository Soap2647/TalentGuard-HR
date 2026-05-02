# Veritabanı Şema Dökümantasyonu

## ER Genel Bakış

```
                ┌──────────────┐
                │ departments  │◄────┐
                └──────┬───────┘     │
                       │             │
                       │ FK          │ FK (manager.dept)
                       ▼             │
   ┌─────────────────────────┐       │
   │ employees                │      │
   │ (PK: id, UQ: emp_number) │      │
   └────┬──────────┬──────────┘      │
        │          │                 │
   FK   │          │ FK              │
        ▼          ▼                 │
   ┌────────┐  ┌─────────────────┐   │
   │job_roles│  │employee_metrics│   │
   └────────┘  │ (1:N zaman ser)│   │
               └─────────────────┘   │
                                     │
   ┌──────────────┐         ┌────────┴────┐
   │predictions   │◄────────│ users       │
   │ JSONB shap   │ FK uid  │ role/dept   │
   └──────┬───────┘         └─────────────┘
          │ FK model_id
          ▼
   ┌──────────────┐
   │model_registry│
   │ JSONB metrics│
   └──────────────┘

   ┌──────────────┐
   │ audit_log    │  ← TÜM trigger'lardan otomatik dolar
   │ JSONB old/new│
   └──────────────┘
```

## Tablolar (3NF)

### `users`
Sistem kullanıcıları + RBAC. `role` CHECK ile {admin, hr, manager} ile sınırlı. `department_id` manager'ın ölçek kapsamını belirler.

### `departments`, `job_roles`
Master tablolar. `employees` bunlara FK ile bağlanır.

### `employees`
Ana iş tablosu. Çalışanın profil bilgileri (yaş, cinsiyet, eğitim, kıdem). `attrition` geçmiş etiket olup ML training için kullanılır. Hesaplanan değerler tutulmaz (3NF).

### `employee_metrics`
Performans, maaş, memnuniyet gibi **zamanla değişen** alanlar. `(employee_id, snapshot_date)` UNIQUE — bir günde bir snapshot.

### `model_registry`
Eğitilen ML modellerinin kaydı. `metrics` JSONB ile esneklik (yeni metrik eklenebilir). `is_active` partial unique index ile aynı anda yalnız 1 kayıt aktif.

### `predictions`
ML çıktıları + `shap_values` JSONB. GIN index ile JSON içinde feature araması mümkün. `model_id` ile hangi model üretti izlenebilir.

### `audit_log`
Trigger'lar tarafından otomatik dolar. `old_data` ve `new_data` JSONB olarak satırın tüm hâlini saklar.

## View'lar

| View | Amaç |
|---|---|
| `v_high_risk_employees` | En güncel tahmine göre risk_level = 'high' olan çalışanlar |
| `v_department_attrition_rate` | Departman bazında yüzdesel attrition oranı |
| `v_monthly_predictions` | Aylık tahmin sayısı + risk dağılımı (trend için) |
| `v_employee_overview` | Çalışan + son metrik + son tahmin (frontend listesi için denormalize) |

## Stored Functions

| Fonksiyon | Dönüş | Amaç |
|---|---|---|
| `fn_attrition_rate_by_dept(dept_id)` | NUMERIC | Tek departman için oran |
| `fn_dashboard_kpis()` | TABLE | Dashboard'un 4 KPI'ı tek çağrıda |
| `fn_risk_level(prob)` | VARCHAR | Olasılığı low/medium/high'a çevirir |
| `fn_employee_risk_history(emp_id)` | TABLE | Bir çalışanın tüm tahmin geçmişi |

## Trigger'lar

### Audit Trigger (`fn_audit_trigger`)
- `employees`, `users`, `predictions`, `model_registry` üzerinde
- `AFTER INSERT/UPDATE/DELETE FOR EACH ROW`
- `to_jsonb(OLD/NEW)` ile satırın tamamını JSONB olarak loglar
- `current_setting('app.current_user', true)` ile FastAPI session var'dan kullanıcıyı yakalar
- DELETE'te NEW null, INSERT'te OLD null

### `fn_set_updated_at`
- `users` ve `employees` üzerinde `BEFORE UPDATE`
- `updated_at` alanını `CURRENT_TIMESTAMP` ile günceller — uygulama tarafına bırakılmaz

## Index Stratejisi

| Index | Tür | Gerekçe |
|---|---|---|
| `idx_employees_department` | B-tree | Departman filtreli sorgular sık |
| `idx_employees_attrition` | B-tree | ML training pull sorgusu |
| `idx_predictions_employee` | B-tree | "bu çalışanın son tahmini" join'i |
| `idx_predictions_created` | B-tree DESC | "en son N tahmin" tarihsel sorguları |
| `idx_predictions_shap_gin` | GIN | JSONB içinde feature aramak (ileride) |
| `uniq_active_model` | Partial UNIQUE | Aynı anda yalnız 1 aktif model |

## Constraint Özeti

- `CHECK`: age 18-70, gender enum, role enum, salary > 0, satisfaction 1-4...
- `UNIQUE`: username, email, employee_number, model_version
- `FK CASCADE`: employee silindiğinde metric ve prediction da silinir
- `FK RESTRICT`: kayıtlı çalışanı olan departman silinemez
- `FK SET NULL`: silinen kullanıcının ürettiği prediction'lar korunur ama created_by = NULL

## Audit Trigger Akışı

```
[FastAPI request]
   ↓
[deps.get_current_user] → JWT decode, user yüklenir
   ↓
[set_audit_user(db, "admin")] → SELECT set_config('app.current_user', 'admin', false)
   ↓
[ORM: db.commit() bir UPDATE/INSERT/DELETE üretir]
   ↓
[PostgreSQL trigger fn_audit_trigger çalışır]
   ↓
[current_setting('app.current_user') = 'admin' okunur]
   ↓
[INSERT INTO audit_log (...) VALUES (...)]
```

## Örnek Sorgular

```sql
-- En son 10 yüksek riskli çalışan
SELECT * FROM v_high_risk_employees LIMIT 10;

-- Sales departmanının attrition oranı
SELECT fn_attrition_rate_by_dept(
    (SELECT id FROM departments WHERE name = 'Sales')
);

-- Dashboard KPI'ları
SELECT * FROM fn_dashboard_kpis();

-- "OverTime" feature'ı SHAP top'ta olan tahminler
SELECT id, employee_id, churn_prob
FROM predictions
WHERE shap_values @> '{"top_features": [{"feature": "cat__overtime_True"}]}'::jsonb;

-- Belirli çalışanın audit geçmişi
SELECT operation, changed_by, changed_at, new_data->>'monthly_income' AS new_income
FROM audit_log
WHERE table_name = 'employees' AND record_id = 42
ORDER BY changed_at DESC;
```

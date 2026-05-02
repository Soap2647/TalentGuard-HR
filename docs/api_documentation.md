# API Dökümantasyonu

> Tüm endpoint'ler `/api` ön ekiyle çalışır. Auth gerektiren endpoint'ler `Authorization: Bearer <token>` bekler.
> Otomatik üretilen Swagger: **http://localhost:8000/docs**

## Auth

### `POST /api/auth/login`
```json
// Body
{ "username": "admin", "password": "admin123" }

// Response 200
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "role": "admin",
  "full_name": "Admin User",
  "username": "admin"
}
```

### `GET /api/auth/me`
Mevcut kullanıcı bilgisi.

## Employees

| Endpoint | Method | Roller | Açıklama |
|---|---|---|---|
| `/api/employees` | GET | tümü | Liste (q, department_id, risk, limit, offset) — manager kendi dept'ine kilitli |
| `/api/employees/{id}` | GET | tümü | Detay + son metric + risk geçmişi |
| `/api/employees` | POST | admin, hr | Yeni çalışan |
| `/api/employees/{id}` | PATCH | admin, hr | Güncelle |
| `/api/employees/{id}` | DELETE | admin | Sil (cascade ile metric + prediction silinir) |
| `/api/employees/{id}/metrics` | POST | admin, hr | Yeni metric snapshot |
| `/api/employees/-/lookups/departments` | GET | tümü | Departman listesi |
| `/api/employees/-/lookups/job_roles` | GET | tümü | Pozisyon listesi |

## Predictions

| Endpoint | Method | Roller | Açıklama |
|---|---|---|---|
| `/api/predictions/adhoc` | POST | tümü | Form girişiyle anlık tahmin (DB'ye yazmaz) |
| `/api/predictions/employee/{id}` | POST | tümü | Çalışan için tahmin + DB'ye kaydet |
| `/api/predictions/batch` | POST | admin, hr | Tüm çalışanlar için toplu tahmin |

### `POST /api/predictions/adhoc` body örneği
```json
{
  "age": 35, "gender": "Male", "marital_status": "Married",
  "education": 3, "education_field": "Life Sciences",
  "department": "Research & Development", "job_role": "Research Scientist",
  "business_travel": "Travel_Rarely",
  "distance_from_home": 5,
  "years_at_company": 5, "years_in_current_role": 3,
  "years_since_last_promotion": 1, "years_with_curr_manager": 3,
  "total_working_years": 10, "num_companies_worked": 2,
  "monthly_income": 5000, "percent_salary_hike": 13,
  "stock_option_level": 1,
  "job_satisfaction": 3, "environment_satisfaction": 3,
  "relationship_satisfaction": 3, "work_life_balance": 3,
  "job_involvement": 3, "performance_rating": 3,
  "training_times_last_year": 2, "overtime": false
}
```

### Response
```json
{
  "churn_prob": 0.6234,
  "risk_level": "medium",
  "model_version": "v_20260426_142055_xgboost",
  "shap_values": {
    "top_features": [
      { "feature": "cat__overtime_True", "shap": 0.4123 },
      { "feature": "num__monthly_income", "shap": -0.2871 },
      { "feature": "num__years_at_company", "shap": 0.1934 },
      { "feature": "num__job_satisfaction", "shap": -0.1502 },
      { "feature": "cat__business_travel_Travel_Frequently", "shap": 0.1244 }
    ]
  }
}
```

## Dashboard

| Endpoint | Method | Açıklama |
|---|---|---|
| `/api/dashboard/kpis` | GET | 4 ana KPI (`fn_dashboard_kpis()`) |
| `/api/dashboard/department-attrition` | GET | `v_department_attrition_rate` |
| `/api/dashboard/monthly-predictions` | GET | Son 12 ay |
| `/api/dashboard/high-risk` | GET | `v_high_risk_employees LIMIT N` |
| `/api/dashboard/risk-distribution` | GET | Pie chart için low/medium/high count |

## Admin (sadece `admin` rolü)

| Endpoint | Method | Açıklama |
|---|---|---|
| `/api/admin/users` | GET | Tüm kullanıcılar |
| `/api/admin/users` | POST | Yeni kullanıcı |
| `/api/admin/users/{id}` | DELETE | Sil |
| `/api/admin/audit-log` | GET | Audit log (table filtresi opsiyonel) |
| `/api/admin/models` | GET | Model versiyon listesi |
| `/api/admin/models/{id}/activate` | POST | Belirli versiyonu aktive et |
| `/api/admin/models/retrain` | POST | Yeni model eğit (sync) |

## Hata Kodları

| Kod | Anlam |
|---|---|
| 400 | Geçersiz request (örn: zaten kayıtlı employee_number) |
| 401 | Auth gerekli / token süresi dolmuş |
| 403 | Yetki yok (rol uyuşmazlığı veya manager kapsam dışı) |
| 404 | Kayıt yok |
| 503 | Aktif model yok (önce `python -m ml.train`) |

## Curl Örnekleri

```bash
# Login
TOKEN=$(curl -s -X POST localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r .access_token)

# Çalışan listesi (yüksek riskli)
curl -H "Authorization: Bearer $TOKEN" "localhost:8000/api/employees?risk=high&limit=10"

# Tek çalışan için tahmin
curl -X POST -H "Authorization: Bearer $TOKEN" "localhost:8000/api/predictions/employee/1"

# Batch tahmin
curl -X POST -H "Authorization: Bearer $TOKEN" "localhost:8000/api/predictions/batch"

# Audit log
curl -H "Authorization: Bearer $TOKEN" "localhost:8000/api/admin/audit-log?table=employees&limit=20"
```

# Çalışan Churn Tahmin Sistemi — Proje Raporu

**Ders:** Veri Tabanı Yönetim Sistemleri
**Dönem:** 2025-2026 Bahar
**Hazırlayan:** _[Ad Soyad - Numara]_

---

## 1. Problem Tanımı

Çalışan turnover (işten ayrılma) hem operasyonel sürekliliği bozar hem de işe alım, eğitim ve verim kaybı yoluyla yüksek finansal maliyet doğurur. Geleneksel HR raporlaması olayları **olduktan sonra** tespit eder; bu projede amaç, çalışan profili ve operasyonel verilerden **olasılık tabanlı erken uyarı** üreten bir sistem kurmaktır.

Sistem 3 ana bileşenden oluşur:
1. **Veritabanı** (sistemin omurgası): normalize şema, view, trigger, audit log, RBAC.
2. **Backend API**: yetkilendirme + CRUD + ML servisi.
3. **Frontend**: KPI dashboard, çalışan analitiği, what-if predict, admin panelleri.

## 2. Kullanılan Teknolojiler

| Katman | Seçim | Gerekçe |
|---|---|---|
| Veritabanı | **PostgreSQL 16** | JSONB, GIN index, partial unique index, güçlü trigger desteği |
| ORM | SQLAlchemy 2.0 | Type-hint dostu, raw SQL ile kolay karışım |
| Backend | FastAPI | Otomatik OpenAPI, async-ready, pydantic ile validation |
| ML | XGBoost + SHAP | Tablolar veride state-of-art, açıklanabilirlik |
| Frontend | React + Vite + Tailwind + Recharts | Modern UX, hızlı build, hafif |
| Auth | JWT (HS256) + bcrypt | Stateless, ölçeklenebilir |

## 3. Veritabanı Tasarımı

### 3.1 Normalleştirme
Tüm tablolar 3NF'tedir. Departman ve pozisyon bilgisi master tablolara çıkarıldı; çalışanın değişen değerleri (maaş, memnuniyet, performans) `employee_metrics` tablosuna zaman serili olarak ayrıldı. Bu sayede tarihsel snapshot saklamak ve "geçen yıla göre bu yıl" tipi sorgular mümkündür.

### 3.2 İleri DBMS Özellikleri
- **4 View**: dashboard ve liste sorgularını sadeleştirir, denormalize çıktı sağlar
- **4 Stored Function** (PL/pgSQL): KPI hesaplama, risk seviyesi, departman attrition oranı, çalışan risk geçmişi
- **5 Trigger**: 4 audit + 1 generic `updated_at`
- **JSONB + GIN**: SHAP değerleri ve model metrikleri esnek şemalı tutulur
- **Partial Unique Index**: aynı anda yalnızca 1 model aktif

### 3.3 RBAC ve Audit
PostgreSQL session var (`app.current_user`) FastAPI middleware'inde set edilir; trigger bu değeri okuyarak audit_log'a "kim değiştirdi" bilgisini yazar. Bu sayede uygulama-veritabanı arası kullanıcı bilgisi güvenli şekilde aktarılır.

`employees` tablosunda manager rolündeki kullanıcı SQL `WHERE department_id = :user_dep` ile **row-level filter**'a uğrar.

## 4. Sistem Mimarisi

(README.md'deki mimari diyagramı buraya ekleyin)

## 5. ML Pipeline

1. **Veri Çekme**: SQL JOIN ile employees + departments + job_roles + en güncel metric birleştirilir
2. **Preprocessing**: 19 numeric feature StandardScaler ile, 7 categorical feature OneHotEncoder ile dönüştürülür
3. **Model Karşılaştırma**: LogReg, RandomForest, XGBoost cross-validate edilir; ROC-AUC en yüksek olan kazanır
4. **Registry**: Joblib ile diske + `model_registry` tablosuna metric ve feature listesi
5. **Serving**: `lru_cache` ile aktif model bellekte tutulur; SHAP TreeExplainer ile top-5 feature
6. **Persistance**: Her tahmin `predictions` tablosuna JSONB SHAP değeriyle yazılır

## 6. Sonuçlar (Beklenen)

IBM HR Analytics dataset'i (1470 satır, %16 pozitif sınıf) üzerinde:
- LogReg: ROC-AUC ~0.78
- RandomForest: ROC-AUC ~0.82
- XGBoost: ROC-AUC ~0.84

(Çalıştırıp gerçek değerleri buraya yazın — `python -m ml.train` çıktısı)

## 7. Kullanıcı Arayüzü

8 sayfa: Login, Dashboard, Çalışanlar, Çalışan Detay, Predict, Model Yönetimi, Audit Log, Kullanıcılar. Dark mode + responsive sidebar layout. Recharts ile bar/line/pie + custom SHAP waterfall.

(Ekran görüntülerini buraya ekleyin: docs/screenshots/)

## 8. Güçlü Yönler & Bonuslar

- ✅ View / SP / Trigger / JSONB / GIN / Partial Index gibi **ileri DB özellikleri** kullanıldı
- ✅ Audit log + RBAC gerçek dünyada compliance gereksinimini karşılar
- ✅ SHAP ile model şeffaflığı (XAI)
- ✅ Model registry ile MLOps best practice
- ✅ OpenAPI otomatik dökümantasyon
- ✅ pytest ile temel testler

## 9. Gelecek Çalışmalar

- Feature engineering: tenure-to-promotion ratio, manager change frequency
- AutoML / hyperparameter optimization (Optuna)
- Real-time streaming (Kafka → predict)
- A/B test çerçevesi (champion/challenger)
- Dashboard'a "what-if" simülasyonu (maaş +%10 → risk değişimi)
- Excel/PDF export raporlama
- Docker compose ile tek-komut deploy

## 10. Kaynaklar

- IBM HR Analytics Employee Attrition Dataset (Kaggle)
- "A Unified Approach to Interpreting Model Predictions", Lundberg & Lee, 2017 (SHAP)
- PostgreSQL 16 Documentation — Triggers, JSONB, Indexing
- FastAPI Documentation — Dependency Injection, Security
- Chen & Guestrin, "XGBoost: A Scalable Tree Boosting System", 2016

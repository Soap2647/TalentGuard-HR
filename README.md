<div align="center">
  <h1>🛡️ TalentGuard HR Analytics</h1>
  <p><strong>Predictive Employee Retention & HR Analytics Platform</strong></p>
  
  [![React](https://img.shields.io/badge/React-18.x-blue.svg?style=flat&logo=react)](https://reactjs.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
  [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16.x-336791.svg?style=flat&logo=postgresql)](https://www.postgresql.org/)
  [![TailwindCSS](https://img.shields.io/badge/Tailwind-3.x-38B2AC.svg?style=flat&logo=tailwind-css)](https://tailwindcss.com/)
  [![Machine Learning](https://img.shields.io/badge/ML-XGBoost%20%7C%20SHAP-FF6F00.svg?style=flat)]()
</div>

---

## 🇬🇧 English

TalentGuard is an enterprise-grade Human Resources application focused on predicting and analyzing employee churn (attrition) using machine learning. Originally built as a comprehensive Database Management Systems project, it leverages a robust 3NF normalized PostgreSQL schema, intelligent ML pipelines, and a modern "glassmorphism" React interface.

### ✨ Key Features
- **Predictive Analytics:** Uses XGBoost and SHAP values to predict the likelihood of employee churn and explains the top risk factors.
- **Modern Glassmorphism UI:** Built with React, Tailwind CSS, Recharts, and custom animations for a premium user experience (including seamless Dark Mode).
- **Role-Based Access Control (RBAC):** Distinct privileges for Admins, HR Specialists, and Department Managers implemented via JWT and row-level data filtering.
- **Advanced Database Architecture:** Fully normalized 3NF PostgreSQL schema utilizing Views, Stored Procedures, Triggers, and JSONB/GIN indexes.
- **Comprehensive Audit Logging:** Database-level tracking of all critical INSERT/UPDATE/DELETE operations.
- **Model Registry System:** Built-in ML versioning, allowing dynamic retraining and model activation.

### 🚀 Tech Stack
- **Frontend:** React, TypeScript, Vite, Tailwind CSS, Recharts, Lucide Icons.
- **Backend:** FastAPI, SQLAlchemy (ORM), Pydantic, Python 3.10+.
- **Database:** PostgreSQL 16 (Relational & Semi-structured data handling).
- **Machine Learning:** Scikit-Learn, XGBoost, SHAP.

### 🛠️ Quick Start

```bash
# 1. Database Setup
createdb -U postgres churn_db

# 2. Backend Initialization
cd backend
python -m venv venv && source venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env

python -m scripts.init_db            # Initialize schema, views, triggers
python -m ml.train                   # Train ML models and activate the best one
uvicorn app.main:app --reload        # Runs on http://localhost:8000

# 3. Frontend Initialization
cd frontend
npm install
npm run dev                          # Runs on http://localhost:5173
```

---

## 🇹🇷 Türkçe

TalentGuard, makine öğrenimi kullanarak çalışanların işten ayrılma (churn) olasılığını tahmin etmeye ve analiz etmeye odaklanan kurumsal düzeyde bir İnsan Kaynakları uygulamasıdır. Başlangıçta kapsamlı bir Veritabanı Yönetim Sistemleri projesi olarak geliştirilmiş olup, 3NF normalize PostgreSQL şeması, akıllı ML ardışık işlemleri ve modern "glassmorphism" React arayüzü üzerine inşa edilmiştir.

### ✨ Temel Özellikler
- **Tahmine Dayalı Analitik:** Çalışanların ayrılma olasılığını tahmin etmek ve en önemli risk faktörlerini açıklamak için XGBoost ve SHAP değerlerini kullanır.
- **Modern Glassmorphism Arayüzü:** Premium bir kullanıcı deneyimi için (kusursuz Karanlık Mod dahil) React, Tailwind CSS, Recharts ve özel animasyonlarla oluşturulmuştur.
- **Rol Bazlı Erişim Kontrolü (RBAC):** Admin, İK Uzmanları ve Departman Yöneticileri için JWT ve satır bazlı (row-level) veri filtreleme ile ayrılmış yetkiler.
- **Gelişmiş Veritabanı Mimarisi:** Görünümler (Views), Saklı Yordamlar (Stored Procedures), Tetikleyiciler (Triggers) ve JSONB/GIN indeksleri kullanan tamamen normalize edilmiş 3NF PostgreSQL şeması.
- **Kapsamlı Denetim Günlüğü (Audit Log):** Tüm kritik INSERT/UPDATE/DELETE işlemlerinin veritabanı seviyesinde takip edilmesi.
- **Model Kayıt Sistemi:** Dinamik yeniden eğitim (retrain) ve model aktivasyonuna olanak tanıyan yerleşik ML versiyonlama.

### 🚀 Teknoloji Yığını
- **Frontend:** React, TypeScript, Vite, Tailwind CSS, Recharts, Lucide Icons.
- **Backend:** FastAPI, SQLAlchemy (ORM), Pydantic, Python 3.10+.
- **Veritabanı:** PostgreSQL 16 (İlişkisel ve yarı yapılandırılmış veri yönetimi).
- **Makine Öğrenimi:** Scikit-Learn, XGBoost, SHAP.

### 🛠️ Hızlı Başlangıç

```bash
# 1. Veritabanı Kurulumu
createdb -U postgres churn_db

# 2. Backend Kurulumu
cd backend
python -m venv venv && source venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env

python -m scripts.init_db            # Şema, view ve trigger'ları oluşturur
python -m ml.train                   # ML modellerini eğitir ve en iyisini aktif eder
uvicorn app.main:app --reload        # http://localhost:8000 adresinde çalışır

# 3. Frontend Kurulumu
cd frontend
npm install
npm run dev                          # http://localhost:5173 adresinde çalışır
```

### 🔐 Demo Hesaplar
| Kullanıcı | Şifre | Rol |
|---|---|---|
| `admin` | `admin123` | Tüm Yetkiler |
| `hr_user` | `hr123` | İnsan Kaynakları |
| `manager` | `manager123` | Departman Yöneticisi |

---
> *Bu proje akademik ve eğitim amaçlı tasarlanmış, süreç içerisinde endüstri standardı modern bir arayüzle modernize edilmiştir.*

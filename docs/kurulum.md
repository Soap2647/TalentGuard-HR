# Kurulum Rehberi

## Önkoşullar

| Bileşen | Sürüm | Notlar |
|---|---|---|
| PostgreSQL | 14+ (test edildi: 16) | `psql`, `createdb` PATH'te olmalı |
| Python | 3.11+ | `pip` & `venv` |
| Node.js | 18+ | `npm` veya `pnpm` |

## 1. Veritabanı Hazırlığı

```bash
# PostgreSQL kullanıcısı olarak
psql -U postgres -c "CREATE DATABASE churn_db;"
psql -U postgres -c "CREATE USER churn_user WITH PASSWORD 'churn_pass';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE churn_db TO churn_user;"
```

## 2. Backend Kurulumu

```bash
cd backend

# Sanal ortam
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

# Yapılandırma
cp .env.example .env
# .env dosyasını aç ve DATABASE_URL'i güncelle
# Örn: postgresql://postgres:postgres@localhost:5432/churn_db
```

### 2.1 Şemayı yükle

```bash
python -m scripts.init_db
```

Bu komut sırayla şunları çalıştırır:
- `sql/01_schema.sql`  — tablolar, indexler, constraint'ler
- `sql/02_views.sql`   — 4 view
- `sql/03_triggers.sql` — audit trigger fonksiyonu + 4 trigger
- `sql/04_procedures.sql` — 4 stored function

### 2.2 Demo veriyi yükle

```bash
python -m scripts.seed_db
```

IBM HR Analytics dataset'ini indirir (1470 satır) ve PostgreSQL'e yazar. 3 demo kullanıcı oluşturur (admin, hr_user, manager).

### 2.3 İlk modeli eğit

```bash
python -m ml.train
```

3 algoritmayı (LogReg, RandomForest, XGBoost) deneyip en iyi ROC-AUC'a sahip olanı `model_registry`'e aktif olarak yazar.

### 2.4 Sunucuyu başlat

```bash
uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 3. Frontend Kurulumu

```bash
cd frontend
npm install
npm run dev
```

Tarayıcıda aç: **http://localhost:5173**

## 4. İlk Tahminleri Üret

Frontend'e admin olarak giriş yap → "Model Yönetimi" → **Batch Tahmin** butonu. Tüm çalışanlar için tahmin üretilir, dashboard ve listelerde görünür.

## 5. Sorun Giderme

| Sorun | Çözüm |
|---|---|
| `password authentication failed` | `.env` içindeki DATABASE_URL kullanıcı/şifresini kontrol et |
| `relation "..." does not exist` | `python -m scripts.init_db` çalıştırılmamış |
| `Aktif model bulunamadı` | `python -m ml.train` çalıştırılmamış |
| Frontend'de 401 | Token süresi dolmuş — yeniden login |
| CORS hatası | `.env` `CORS_ORIGINS` ayarına frontend URL'i ekle |

## 6. Test

```bash
cd backend
pytest -v
```

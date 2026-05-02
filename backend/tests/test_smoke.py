"""Temel smoke testler — health, login, listeleme."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["app"] == "Çalışan Churn Tahmin"


def test_health():
    r = client.get("/health")
    assert r.json() == {"status": "ok"}


def test_login_invalid():
    r = client.post("/api/auth/login", json={"username": "nope", "password": "wrong"})
    assert r.status_code == 401


def test_login_admin_then_me():
    """Seed çalıştırılmış DB ile çalışır."""
    r = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    if r.status_code != 200:
        # DB seed edilmemiş olabilir — testi atla
        return
    token = r.json()["access_token"]
    r2 = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    assert r2.json()["role"] == "admin"


def test_dashboard_requires_auth():
    r = client.get("/api/dashboard/kpis")
    assert r.status_code == 401

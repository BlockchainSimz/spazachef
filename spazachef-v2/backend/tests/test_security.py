from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_generation_fails_closed_when_jwt_secret_missing(monkeypatch):
    monkeypatch.delenv("SUPABASE_JWT_SECRET", raising=False)
    response = client.post("/api/recipes/generate", json={"ingredients": "rice, tomato"})
    assert response.status_code == 503

def test_generation_requires_bearer_token(monkeypatch):
    monkeypatch.setenv("SUPABASE_JWT_SECRET", "test-secret-with-enough-entropy")
    response = client.post("/api/recipes/generate", json={"ingredients": "rice, tomato"})
    assert response.status_code == 401

def test_generation_rejects_invalid_token(monkeypatch):
    monkeypatch.setenv("SUPABASE_JWT_SECRET", "test-secret-with-enough-entropy")
    response = client.post("/api/recipes/generate", headers={"Authorization": "Bearer invalid"}, json={"ingredients": "rice, tomato"})
    assert response.status_code == 401

def test_payfast_itn_cannot_grant_tier_while_verification_incomplete():
    response = client.post("/api/payfast/itn", data={"payment_status": "COMPLETE", "amount_gross": "99.00", "custom_str1": "victim"})
    assert response.status_code == 503

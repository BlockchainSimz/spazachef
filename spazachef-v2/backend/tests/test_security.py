import os
import jwt
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
import pytest
from app.main import app, who

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


def test_valid_legacy_supabase_hs256_token_resolves_user(monkeypatch):
    secret = "test-secret-with-enough-entropy"
    monkeypatch.setenv("SUPABASE_JWT_SECRET", secret)
    monkeypatch.setattr("app.main.store.tier", lambda uid: None)
    token = jwt.encode({"sub": "user-123", "aud": "authenticated"}, secret, algorithm="HS256")
    uid, tier = who(None, "Bearer " + token)
    assert uid == "user-123"
    assert tier == "free"


def test_payfast_itn_cannot_grant_tier_while_verification_incomplete():
    response = client.post("/api/payfast/itn", data={"payment_status": "COMPLETE", "amount_gross": "99.00", "custom_str1": "victim"})
    assert response.status_code == 503

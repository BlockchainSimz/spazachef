import jwt
from types import SimpleNamespace
from fastapi.testclient import TestClient
import app.main as main
from app.main import app, who

client = TestClient(app)


def configured(monkeypatch):
    monkeypatch.setattr(main, "SUPABASE_URL", "https://unit-test.supabase.co")
    monkeypatch.setattr(main, "SUPABASE_PUBLISHABLE_KEY", "sb_publishable_test_key")


def test_generation_fails_closed_when_auth_verifier_missing(monkeypatch):
    monkeypatch.setattr(main, "SUPABASE_URL", "")
    monkeypatch.setattr(main, "SUPABASE_PUBLISHABLE_KEY", "")
    response = client.post("/api/recipes/generate", json={"ingredients": "rice, tomato"})
    assert response.status_code == 503


def test_generation_requires_bearer_token(monkeypatch):
    configured(monkeypatch)
    response = client.post("/api/recipes/generate", json={"ingredients": "rice, tomato"})
    assert response.status_code == 401


def test_generation_rejects_invalid_token(monkeypatch):
    configured(monkeypatch)
    response = client.post("/api/recipes/generate", headers={"Authorization": "Bearer invalid"}, json={"ingredients": "rice, tomato"})
    assert response.status_code == 401


def test_valid_legacy_supabase_hs256_token_is_checked_with_auth_server(monkeypatch):
    configured(monkeypatch)
    token = jwt.encode({"sub": "user-123", "aud": "authenticated"}, "dummy-test-signature", algorithm="HS256")
    captured = {}
    def fake_get(url, headers, timeout):
        captured.update(url=url, headers=headers, timeout=timeout)
        return SimpleNamespace(status_code=200, json=lambda: {"id": "user-123"})
    monkeypatch.setattr(main.httpx, "get", fake_get)
    uid, tier = who(None, "Bearer " + token)
    assert (uid, tier) == ("user-123", "free")
    assert captured["url"] == "https://unit-test.supabase.co/auth/v1/user"
    assert captured["headers"]["apikey"] == "sb_publishable_test_key"


def test_auth_server_rejects_invalid_legacy_token(monkeypatch):
    configured(monkeypatch)
    token = jwt.encode({"sub": "user-123"}, "dummy-test-signature", algorithm="HS256")
    monkeypatch.setattr(main.httpx, "get", lambda *a, **k: SimpleNamespace(status_code=401, json=lambda: {}))
    try:
        who(None, "Bearer " + token)
        assert False, "Expected invalid token to be rejected"
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 401


def test_payfast_itn_cannot_grant_tier_while_verification_incomplete():
    response = client.post("/api/payfast/itn", data={"payment_status": "COMPLETE", "amount_gross": "99.00", "custom_str1": "victim"})
    assert response.status_code == 503

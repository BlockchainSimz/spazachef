import jwt
from fastapi.testclient import TestClient
from app.main import app, who

client = TestClient(app)


def configure_auth(monkeypatch):
    monkeypatch.setattr("app.main.SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setattr("app.main.SUPABASE_PUBLISHABLE_KEY", "sb_publishable_test")


def test_generation_fails_closed_when_supabase_auth_config_missing(monkeypatch):
    monkeypatch.setattr("app.main.SUPABASE_URL", "")
    monkeypatch.setattr("app.main.SUPABASE_PUBLISHABLE_KEY", "")
    response = client.post("/api/recipes/generate", json={"ingredients": "rice, tomato"})
    assert response.status_code == 503


def test_generation_requires_bearer_token(monkeypatch):
    configure_auth(monkeypatch)
    response = client.post("/api/recipes/generate", json={"ingredients": "rice, tomato"})
    assert response.status_code == 401


def test_generation_rejects_invalid_token(monkeypatch):
    configure_auth(monkeypatch)
    response = client.post(
        "/api/recipes/generate",
        headers={"Authorization": "Bearer invalid"},
        json={"ingredients": "rice, tomato"},
    )
    assert response.status_code == 401


def test_valid_legacy_supabase_hs256_token_resolves_user(monkeypatch):
    configure_auth(monkeypatch)
    token = jwt.encode(
        {"sub": "user-123", "aud": "authenticated"},
        "not-used-for-verification",
        algorithm="HS256",
    )

    class AuthResponse:
        status_code = 200

        @staticmethod
        def json():
            return {"id": "user-123"}

    monkeypatch.setattr("app.main.httpx.get", lambda *args, **kwargs: AuthResponse())
    monkeypatch.setattr("app.main.store.tier", lambda uid: None)
    uid, tier = who(None, "Bearer " + token)
    assert uid == "user-123"
    assert tier == "free"


def test_hs256_token_subject_must_match_auth_user(monkeypatch):
    configure_auth(monkeypatch)
    token = jwt.encode({"sub": "attacker", "aud": "authenticated"}, "test", algorithm="HS256")

    class AuthResponse:
        status_code = 200

        @staticmethod
        def json():
            return {"id": "victim"}

    monkeypatch.setattr("app.main.httpx.get", lambda *args, **kwargs: AuthResponse())
    try:
        who(None, "Bearer " + token)
        assert False, "Expected identity mismatch to be rejected"
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 401


def test_database_failure_is_not_misreported_as_invalid_token(monkeypatch):
    configure_auth(monkeypatch)
    token = jwt.encode({"sub": "user-123", "aud": "authenticated"}, "test", algorithm="HS256")

    class AuthResponse:
        status_code = 200

        @staticmethod
        def json():
            return {"id": "user-123"}

    monkeypatch.setattr("app.main.httpx.get", lambda *args, **kwargs: AuthResponse())

    def unavailable(_uid):
        raise RuntimeError("database unavailable")

    monkeypatch.setattr("app.main.store.tier", unavailable)
    try:
        who(None, "Bearer " + token)
        assert False, "Expected database failure to return 503"
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 503


def test_payfast_itn_cannot_grant_tier_while_verification_incomplete():
    response = client.post(
        "/api/payfast/itn",
        data={"payment_status": "COMPLETE", "amount_gross": "99.00", "custom_str1": "victim"},
    )
    assert response.status_code == 503

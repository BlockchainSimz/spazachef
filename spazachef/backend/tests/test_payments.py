from fastapi.testclient import TestClient
from urllib.parse import urlencode

from app import main, store


def configure_payfast(monkeypatch, tmp_path):
    monkeypatch.setattr(store, "_PATH", str(tmp_path / "payments.db"))
    monkeypatch.setenv("ENV", "development")
    monkeypatch.setenv("PAYFAST_MERCHANT_ID", "10000100")
    monkeypatch.setenv("PAYFAST_MERCHANT_KEY", "test-merchant-key")
    monkeypatch.setenv("PAYFAST_PASSPHRASE", "test-passphrase")
    monkeypatch.setenv("PAYFAST_RETURN_URL", "https://app.example.test/paid")
    monkeypatch.setenv("PAYFAST_CANCEL_URL", "https://app.example.test/cancel")
    monkeypatch.setenv("PAYFAST_NOTIFY_URL", "https://api.example.test/api/payfast/itn")
    monkeypatch.setenv("PAYFAST_SANDBOX", "true")


def test_checkout_is_server_signed_and_persists_the_order(monkeypatch, tmp_path):
    configure_payfast(monkeypatch, tmp_path)
    with TestClient(main.app) as client:
        response = client.post("/api/payfast/checkout", json={"tier": "basic", "email": "cook@example.test"})

    assert response.status_code == 200
    checkout = response.json()
    fields = checkout["fields"]
    signature, _ = main.payfast_signature(list(fields.items()), "test-passphrase")
    assert checkout["action"] == "https://sandbox.payfast.co.za/eng/process"
    assert fields["merchant_id"] == "10000100"
    assert fields["amount"] == "15.00"
    assert fields["custom_str1"] == "dev:local"
    assert fields["signature"] == signature
    assert store.tier("dev:local") is None
    assert store.record_payment("pf-1", fields["m_payment_id"], "dev:local", "basic", "15.00")
    assert store.tier("dev:local") == "basic"


def test_payment_is_idempotent_and_must_match_checkout_order(monkeypatch, tmp_path):
    configure_payfast(monkeypatch, tmp_path)
    store.create_checkout_order("order-1", "user-1", "premium", "99.00")
    store.create_checkout_order("order-2", "user-1", "premium", "99.00")

    assert store.record_payment("pf-1", "order-1", "user-1", "premium", "99.00")
    assert store.record_payment("pf-1", "order-1", "user-1", "premium", "99.00")
    assert not store.record_payment("pf-1", "order-2", "user-1", "premium", "99.00")
    assert not store.record_payment("pf-2", "order-1", "user-1", "basic", "15.00")
    assert not store.record_payment("pf-3", "unknown-order", "user-1", "premium", "99.00")
    assert store.tier("user-1") == "premium"
    assert store.tier("attacker") is None


def test_checkout_rejects_unknown_tiers(monkeypatch, tmp_path):
    configure_payfast(monkeypatch, tmp_path)
    with TestClient(main.app) as client:
        response = client.post("/api/payfast/checkout", json={"tier": "enterprise", "email": "cook@example.test"})

    assert response.status_code == 422


def test_itn_verifies_with_payfast_and_applies_matching_order(monkeypatch, tmp_path):
    configure_payfast(monkeypatch, tmp_path)

    class FakeResponse:
        status_code = 200
        text = "VALID"

    class FakeAsyncClient:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def post(self, url, **kwargs):
            assert url == "https://sandbox.payfast.co.za/eng/query/validate"
            return FakeResponse()

    monkeypatch.setattr(main.httpx, "AsyncClient", FakeAsyncClient)
    with TestClient(main.app) as client:
        checkout = client.post("/api/payfast/checkout", json={"tier": "basic", "email": "cook@example.test"}).json()
        fields = checkout["fields"]
        pairs = [
            ("m_payment_id", fields["m_payment_id"]),
            ("pf_payment_id", "pf-100"),
            ("payment_status", "COMPLETE"),
            ("item_name", "SpazaChef Basic"),
            ("amount_gross", "15.00"),
            ("custom_str1", "dev:local"),
            ("merchant_id", "10000100"),
        ]
        signature, _ = main.payfast_signature(pairs, "test-passphrase")
        payload = urlencode(pairs + [("signature", signature)])
        response = client.post("/api/payfast/itn", content=payload, headers={"Content-Type": "application/x-www-form-urlencoded"})
        assert response.status_code == 200
        assert store.tier("dev:local") == "basic"

        wrong_order = pairs.copy()
        wrong_order[0] = ("m_payment_id", "not-a-real-order")
        signature, _ = main.payfast_signature(wrong_order, "test-passphrase")
        rejected = client.post(
            "/api/payfast/itn",
            content=urlencode(wrong_order + [("signature", signature)]),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert rejected.status_code == 400


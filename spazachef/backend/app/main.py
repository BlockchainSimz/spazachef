"""SpazaChef HTTP API."""
import hashlib
import hmac
import os
import datetime as dt
import uuid
from contextlib import asynccontextmanager
from urllib.parse import parse_qsl, quote_plus

import httpx
import jwt
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import engine, store

QUOTA = {"free": 5, "basic": 30, "premium": 10_000}
PRICE_TIER = {"15.00": "basic", "99.00": "premium"}
TIER_PRICE = {tier: amount for amount, tier in PRICE_TIER.items()}
ENV = os.getenv("ENV", "development").lower()
IS_PRODUCTION = ENV == "production"


def configured_origins() -> list[str]:
    values = [value.strip().rstrip("/") for value in os.getenv("ORIGINS", "http://localhost:5173").split(",")]
    if not values or any(not value for value in values):
        raise RuntimeError("ORIGINS must contain one or more explicit origins")
    if IS_PRODUCTION and any(not value.startswith("https://") for value in values):
        raise RuntimeError("Production ORIGINS must use HTTPS")
    return values


@asynccontextmanager
async def lifespan(_app):
    validate_production_configuration()
    yield


app = FastAPI(
    title="SpazaChef API",
    docs_url=None if IS_PRODUCTION else "/docs",
    redoc_url=None if IS_PRODUCTION else "/redoc",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=configured_origins(),
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
    allow_credentials=False,
    max_age=600,
)


def validate_production_configuration() -> None:
    if not IS_PRODUCTION:
        return
    if not os.getenv("SUPABASE_JWT_SECRET"):
        raise RuntimeError("SUPABASE_JWT_SECRET is required in production")
    if not os.getenv("SUPABASE_JWT_ISSUER"):
        raise RuntimeError("SUPABASE_JWT_ISSUER is required in production")
    path = os.getenv("DATABASE_PATH", "")
    if not path or not os.path.isabs(path):
        raise RuntimeError("DATABASE_PATH must be an absolute path to persistent storage in production")
    payment_configuration = (
        "PAYFAST_MERCHANT_ID", "PAYFAST_MERCHANT_KEY", "PAYFAST_PASSPHRASE",
        "PAYFAST_RETURN_URL", "PAYFAST_CANCEL_URL", "PAYFAST_NOTIFY_URL",
    )
    if any(not os.getenv(key) for key in payment_configuration):
        raise RuntimeError("PayFast credentials and callback URLs are required in production")
    for key in ("PAYFAST_RETURN_URL", "PAYFAST_CANCEL_URL", "PAYFAST_NOTIFY_URL"):
        if not os.getenv(key, "").startswith("https://"):
            raise RuntimeError(f"{key} must use HTTPS in production")
    store.initialize()


def who(authorization: str | None) -> tuple[str, str]:
    secret = os.getenv("SUPABASE_JWT_SECRET")
    if not authorization:
        if IS_PRODUCTION:
            raise HTTPException(401, "Sign in to continue.")
        return "dev:local", "free"
    if not secret:
        raise HTTPException(503, "Authentication is not configured.")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(401, "Use a valid bearer token.")
    options = {"require": ["exp", "sub", "aud"]}
    decode_args = {"algorithms": ["HS256"], "audience": "authenticated", "options": options}
    issuer = os.getenv("SUPABASE_JWT_ISSUER")
    if issuer:
        decode_args["issuer"] = issuer
    try:
        claims = jwt.decode(token, secret, **decode_args)
        uid = claims.get("sub")
        if not isinstance(uid, str) or not uid:
            raise jwt.InvalidTokenError("Missing subject")
    except jwt.PyJWTError as exc:
        raise HTTPException(401, "Your session is invalid or expired. Sign in again.") from exc
    tier = store.tier(uid) or claims.get("app_metadata", {}).get("tier", "free")
    return uid, tier if tier in QUOTA else "free"


class Brief(BaseModel):
    persona: str = Field("zanele", pattern="^(zanele|jabu|farah|raj)$")
    ingredients: str = Field(min_length=2, max_length=2000)
    diet: str = Field("", max_length=60)
    serves: int = Field(4, ge=1, le=20)
    notes: str = Field("", max_length=200)


class Feedback(BaseModel):
    rating: int | None = Field(None, ge=1, le=5)
    cooked: bool = False
    regenerated: bool = False


class CheckoutRequest(BaseModel):
    tier: str = Field(pattern="^(basic|premium)$")
    email: str = Field(min_length=6, max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def user_id(authorization: str | None) -> tuple[str, str]:
    return who(authorization)


@app.get("/api/health")
def health():
    return {"ok": True}


@app.post("/api/recipes/generate")
def generate(b: Brief, authorization: str | None = Header(None)):
    uid, tier = user_id(authorization)
    if not store.use(uid, dt.date.today().isoformat(), QUOTA.get(tier, 5)):
        raise HTTPException(429, "You've used today's recipe limit. Try again tomorrow.")
    try:
        recipe = engine.generate(b.model_dump(), b.persona, store.weights())
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    store.add_recipe(uid, recipe)
    return recipe


@app.get("/api/recipes")
def mine(authorization: str | None = Header(None)):
    uid, _ = user_id(authorization)
    return store.recipes(uid)


@app.post("/api/recipes/{rid}/feedback")
def feedback(rid: str, f: Feedback, authorization: str | None = Header(None)):
    uid, _ = user_id(authorization)
    recipe = store.get(uid, rid)
    if not recipe:
        raise HTTPException(404, "Recipe not found.")
    store.mark(uid, rid, f.rating, f.cooked)
    store.save_weights(engine.learn(store.weights(), recipe["persona"], recipe["archetype"], f.rating, f.cooked, f.regenerated))
    return {"ok": True}


def payfast_signature(pairs: list[tuple[str, str]], passphrase: str | None) -> tuple[str, str]:
    fields = [(key, value) for key, value in pairs if key != "signature" and value != ""]
    payload = "&".join(f"{key}={quote_plus(value, safe='')}" for key, value in fields)
    if passphrase:
        payload += "&passphrase=" + quote_plus(passphrase, safe="")
    signature = hashlib.md5(payload.encode("utf-8")).hexdigest()
    validation_body = "&".join(f"{key}={quote_plus(value, safe='')}" for key, value in pairs if key != "signature")
    return signature, validation_body


@app.post("/api/payfast/checkout")
def checkout(b: CheckoutRequest, authorization: str | None = Header(None)):
    uid, _ = who(authorization)
    merchant_id = os.getenv("PAYFAST_MERCHANT_ID")
    merchant_key = os.getenv("PAYFAST_MERCHANT_KEY")
    passphrase = os.getenv("PAYFAST_PASSPHRASE")
    if not all((merchant_id, merchant_key, passphrase)):
        raise HTTPException(503, "PayFast checkout is not configured.")

    amount = TIER_PRICE[b.tier]
    order_id = uuid.uuid4().hex
    pairs = [
        ("merchant_id", merchant_id),
        ("merchant_key", merchant_key),
        ("return_url", os.getenv("PAYFAST_RETURN_URL", "")),
        ("cancel_url", os.getenv("PAYFAST_CANCEL_URL", "")),
        ("notify_url", os.getenv("PAYFAST_NOTIFY_URL", "")),
        ("email_address", b.email.strip()),
        ("m_payment_id", order_id),
        ("amount", amount),
        ("item_name", f"SpazaChef {b.tier.title()}"),
        ("custom_str1", uid),
    ]
    signature, _ = payfast_signature(pairs, passphrase)
    store.create_checkout_order(order_id, uid, b.tier, amount)
    fields = dict(pairs)
    fields["signature"] = signature
    host = "sandbox.payfast.co.za" if os.getenv("PAYFAST_SANDBOX", "false").lower() == "true" else "www.payfast.co.za"
    return {"action": f"https://{host}/eng/process", "fields": fields}


@app.post("/api/payfast/itn")
async def itn(req: Request):
    raw = (await req.body()).decode("utf-8", errors="strict")
    pairs = parse_qsl(raw, keep_blank_values=True, strict_parsing=True)
    data: dict[str, str] = {}
    for key, value in pairs:
        if key in data:
            raise HTTPException(400, "Duplicate ITN fields are not accepted.")
        data[key] = value
    merchant = os.getenv("PAYFAST_MERCHANT_ID")
    passphrase = os.getenv("PAYFAST_PASSPHRASE")
    signature, validation_body = payfast_signature(pairs, passphrase)
    if not merchant or not passphrase or not hmac.compare_digest(signature, data.get("signature", "")):
        raise HTTPException(400, "Invalid payment notification.")
    if data.get("merchant_id") != merchant:
        raise HTTPException(400, "Invalid payment notification.")
    tier = PRICE_TIER.get(data.get("amount_gross", ""))
    uid = data.get("custom_str1", "")
    payment_id = data.get("pf_payment_id", "")
    if data.get("payment_status") != "COMPLETE" or not tier or not uid or not payment_id:
        return "OK"

    host = "sandbox.payfast.co.za" if os.getenv("PAYFAST_SANDBOX", "false").lower() == "true" else "www.payfast.co.za"
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(8.0), follow_redirects=False) as client:
            response = await client.post(
                f"https://{host}/eng/query/validate",
                content=validation_body,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
    except httpx.HTTPError as exc:
        raise HTTPException(503, "Payment verification is temporarily unavailable.") from exc
    if response.status_code != 200 or response.text.strip() != "VALID":
        raise HTTPException(400, "Payment verification failed.")
    if not store.record_payment(payment_id, data.get("m_payment_id", ""), uid, tier, data["amount_gross"]):
        raise HTTPException(400, "Payment does not match a pending SpazaChef order.")
    return "OK"


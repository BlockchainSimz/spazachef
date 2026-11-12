import os
import datetime as dt

import httpx
import jwt
from jwt import PyJWKClient
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from . import engine, store

QUOTA = {"free": 5, "basic": 30, "premium": 10_000}
SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
JWKS_CLIENT = (
    PyJWKClient(f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json", cache_keys=True)
    if SUPABASE_URL else None
)

app = FastAPI(
    title="SpazaChef API",
    docs_url=None if os.getenv("ENV", "production").lower() == "production" else "/docs",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv("ORIGINS", "http://localhost:5173").split(",")
        if origin.strip()
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


def who(req: Request, auth):
    """Validate asymmetric JWTs locally and legacy HS256 tokens with Supabase Auth."""
    if not SUPABASE_URL or not SUPABASE_PUBLISHABLE_KEY:
        raise HTTPException(503, "Authentication is not configured. Please try again later.")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(401, "Sign in to continue.")

    token = auth[7:]
    try:
        header = jwt.get_unverified_header(token)
        algorithm = header.get("alg")
        if algorithm in ("ES256", "RS256") and JWKS_CLIENT:
            signing_key = JWKS_CLIENT.get_signing_key_from_jwt(token).key
            claims = jwt.decode(
                token,
                signing_key,
                algorithms=["ES256", "RS256"],
                audience="authenticated",
                issuer=f"{SUPABASE_URL}/auth/v1",
            )
            uid = claims.get("sub")
        elif algorithm == "HS256":
            response = httpx.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={
                    "apikey": SUPABASE_PUBLISHABLE_KEY,
                    "Authorization": f"Bearer {token}",
                },
                timeout=5.0,
            )
            if response.status_code != 200:
                raise HTTPException(401, "Your session is invalid or expired. Sign in again.")
            user = response.json()
            uid = user.get("id")
            unverified_claims = jwt.decode(
                token,
                options={"verify_signature": False, "verify_aud": False, "verify_iss": False},
                algorithms=["HS256"],
            )
            if not uid or uid != unverified_claims.get("sub"):
                raise HTTPException(401, "Your session is invalid. Sign in again.")
        else:
            raise HTTPException(401, "Your session uses an unsupported signing key. Sign in again.")

        if not isinstance(uid, str) or not uid:
            raise HTTPException(401, "Your session is invalid. Sign in again.")
    except HTTPException:
        raise
    except (httpx.TimeoutException, httpx.RequestError) as exc:
        raise HTTPException(503, "Authentication service is temporarily unavailable.") from exc
    except Exception as exc:
        raise HTTPException(401, "Your session is invalid or expired. Sign in again.") from exc

    try:
        tier = store.tier(uid) or "free"
    except Exception as exc:
        raise HTTPException(503, "Database is temporarily unavailable.") from exc
    return uid, tier if tier in QUOTA else "free"


class Brief(BaseModel):
    persona: str = "zanele"
    ingredients: str = Field(min_length=2, max_length=2000)
    diet: str = Field("", max_length=60)
    serves: int = Field(4, ge=1, le=20)
    notes: str = Field("", max_length=200)


class Feedback(BaseModel):
    rating: int | None = Field(None, ge=1, le=5)
    cooked: bool = False
    regenerated: bool = False


@app.get("/api/health")
def health():
    """Liveness probe: confirms that the ASGI process is responding."""
    return {"ok": True}


@app.get("/api/ready")
def readiness():
    """Readiness probe: confirms required production configuration and DB access."""
    if not SUPABASE_URL or not SUPABASE_PUBLISHABLE_KEY:
        raise HTTPException(503, "Authentication service is not configured.")
    try:
        store.ping()
    except Exception as exc:
        raise HTTPException(503, "Database is not ready.") from exc
    return {"ok": True, "database": "ready", "authentication": "configured"}


@app.post("/api/recipes/generate")
def generate(b: Brief, req: Request, authorization: str | None = Header(None)):
    uid, tier = who(req, authorization)
    try:
        if not store.allow_request(uid, "recipe-generate", 10):
            raise HTTPException(429, "Too many recipe requests. Please wait a minute.", headers={"Retry-After": "60"})
        recipe = engine.generate(b.model_dump(), b.persona, store.weights(uid))
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    except Exception as exc:
        raise HTTPException(503, "Recipe service is temporarily unavailable.") from exc
    try:
        if not store.use(uid, dt.date.today().isoformat(), QUOTA.get(tier, 5)):
            raise HTTPException(402, "You've used today's recipe allowance. Upgrade for more.")
        store.add_recipe(uid, recipe)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(503, "Database is temporarily unavailable.") from exc
    return recipe


@app.get("/api/recipes")
def mine(req: Request, authorization: str | None = Header(None)):
    uid, _ = who(req, authorization)
    try:
        if not store.allow_request(uid, "recipe-list", 120):
            raise HTTPException(429, "Too many requests. Please try again shortly.", headers={"Retry-After": "60"})
        return store.recipes(uid)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(503, "Database is temporarily unavailable.") from exc


@app.post("/api/recipes/{rid}/feedback")
def feedback(rid: str, f: Feedback, req: Request, authorization: str | None = Header(None)):
    uid, _ = who(req, authorization)
    try:
        if not store.allow_request(uid, "recipe-feedback", 60):
            raise HTTPException(429, "Too many feedback requests. Please try again shortly.", headers={"Retry-After": "60"})
        recipe = store.get(uid, rid)
        if not recipe:
            raise HTTPException(404, "Recipe not found.")
        store.mark(uid, rid, f.rating, f.cooked)
        store.save_weights(
            uid,
            engine.learn(
                store.weights(uid),
                recipe["persona"],
                recipe["archetype"],
                f.rating,
                f.cooked,
                f.regenerated,
            )
        )
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(503, "Database is temporarily unavailable.") from exc


@app.post("/api/payfast/itn")
async def itn(req: Request):
    raise HTTPException(503, "Payment notifications are temporarily disabled pending secure verification.")

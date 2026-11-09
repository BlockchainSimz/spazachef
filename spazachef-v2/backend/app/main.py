import os, datetime as dt
import jwt
from jwt import PyJWKClient
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from . import engine, store

QUOTA = {"free": 5, "basic": 30, "premium": 10_000}
SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
JWKS_CLIENT = PyJWKClient(f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json", cache_keys=True) if SUPABASE_URL else None
app = FastAPI(title="SpazaChef API", docs_url=None if os.getenv("ENV") == "production" else "/docs")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in os.getenv("ORIGINS", "http://localhost:5173").split(",") if x.strip()],
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

def who(req: Request, auth):
    """Verify Supabase JWTs using project JWKS (asymmetric) or legacy HS256 secret."""
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(401, "Sign in to continue.")
    token = auth[7:]
    try:
        header = jwt.get_unverified_header(token)
        if header.get("alg") in ("ES256", "RS256") and JWKS_CLIENT:
            key = JWKS_CLIENT.get_signing_key_from_jwt(token).key
            claims = jwt.decode(token, key, algorithms=["ES256", "RS256"], audience="authenticated",
                                issuer=f"{SUPABASE_URL}/auth/v1")
        elif header.get("alg") == "HS256" and os.getenv("SUPABASE_JWT_SECRET"):
            claims = jwt.decode(token, os.environ["SUPABASE_JWT_SECRET"], algorithms=["HS256"],
                                audience="authenticated",
                                issuer=f"{SUPABASE_URL}/auth/v1" if SUPABASE_URL else None)
        else:
            raise HTTPException(401, "Your session uses an unsupported signing key. Sign in again.")
        uid = claims.get("sub")
        if not isinstance(uid, str) or not uid:
            raise HTTPException(401, "Your session is invalid. Sign in again.")
        tier = store.tier(uid) or claims.get("app_metadata", {}).get("tier", "free")
        return uid, tier if tier in QUOTA else "free"
    except HTTPException:
        raise
    except Exception as exc:
        # Do not disclose token, key, or verifier internals to the client.
        raise HTTPException(401, "Your session is invalid or expired. Sign in again.") from exc

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
    return {"ok": True}

@app.post("/api/recipes/generate")
def generate(b: Brief, req: Request, authorization: str | None = Header(None)):
    uid, tier = who(req, authorization)
    try:
        recipe = engine.generate(b.model_dump(), b.persona, store.weights())
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    if not store.use(uid, dt.date.today().isoformat(), QUOTA.get(tier, 5)):
        raise HTTPException(402, "You've used today's recipe allowance. Upgrade for more.")
    store.add_recipe(uid, recipe)
    return recipe

@app.get("/api/recipes")
def mine(req: Request, authorization: str | None = Header(None)):
    return store.recipes(who(req, authorization)[0])

@app.post("/api/recipes/{rid}/feedback")
def feedback(rid: str, f: Feedback, req: Request, authorization: str | None = Header(None)):
    uid, _ = who(req, authorization)
    recipe = store.get(uid, rid)
    if not recipe:
        raise HTTPException(404, "Recipe not found.")
    store.mark(uid, rid, f.rating, f.cooked)
    store.save_weights(engine.learn(store.weights(), recipe["persona"], recipe["archetype"], f.rating, f.cooked, f.regenerated))
    return {"ok": True}

@app.post("/api/payfast/itn")
async def itn(req: Request):
    raise HTTPException(503, "Payment notifications are temporarily disabled pending secure verification.")

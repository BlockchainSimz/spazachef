import hashlib, hmac, os, time, datetime as dt
from collections import defaultdict, deque
from urllib.parse import parse_qsl, quote_plus
import jwt
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from . import engine, store

QUOTA = {"free": 5, "basic": 30, "premium": 10_000}  # recipes/day: R0, R15, R99
PRICE_TIER = {"15.00": "basic", "99.00": "premium"}
app = FastAPI(title="SpazaChef API", docs_url=None if os.getenv("ENV") == "production" else "/docs")
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("ORIGINS", "http://localhost:5173").split(","), allow_methods=["*"], allow_headers=["*"])
hits = defaultdict(deque)

def who(req: Request, auth):
    ip = (req.headers.get("x-forwarded-for") or req.client.host).split(",")[0].strip()
    t = hits[ip]; now = time.time()
    while t and now - t[0] > 60: t.popleft()
    if len(t) >= 30: raise HTTPException(429, "Too many requests. Wait a minute and try again.")
    t.append(now)
    secret = os.getenv("SUPABASE_JWT_SECRET")
    if auth and secret:
        try:
            c = jwt.decode(auth.removeprefix("Bearer "), secret, algorithms=["HS256"], audience="authenticated")
            return c["sub"], store.tier(c["sub"]) or c.get("app_metadata", {}).get("tier", "free")
        except jwt.PyJWTError: raise HTTPException(401, "Your session expired. Sign in again.")
    return "ip:" + ip, "free"

class Brief(BaseModel):
    persona: str = "zanele"; ingredients: str = Field(min_length=2, max_length=2000)
    diet: str = Field("", max_length=60); serves: int = Field(4, ge=1, le=20); notes: str = Field("", max_length=200)
class Feedback(BaseModel):
    rating: int | None = Field(None, ge=1, le=5); cooked: bool = False; regenerated: bool = False

@app.get("/api/health")
def health(): return {"ok": True}

@app.post("/api/recipes/generate")
def generate(b: Brief, req: Request, authorization: str | None = Header(None)):
    uid, tier = who(req, authorization)
    if not store.use(uid, dt.date.today().isoformat(), QUOTA.get(tier, 5)):
        raise HTTPException(402, "You've used today's free recipes. Upgrade for more.")
    try: r = engine.generate(b.model_dump(), b.persona, store.weights())
    except ValueError as e: raise HTTPException(422, str(e))
    store.add_recipe(uid, r); return r

@app.get("/api/recipes")
def mine(req: Request, authorization: str | None = Header(None)): return store.recipes(who(req, authorization)[0])

@app.post("/api/recipes/{rid}/feedback")
def feedback(rid: str, f: Feedback, req: Request, authorization: str | None = Header(None)):
    uid, _ = who(req, authorization); r = store.get(uid, rid)
    if not r: raise HTTPException(404, "Recipe not found.")
    store.mark(uid, rid, f.rating, f.cooked)
    store.save_weights(engine.learn(store.weights(), r["persona"], r["archetype"], f.rating, f.cooked, f.regenerated)); return {"ok": True}

@app.post("/api/payfast/itn")
async def itn(req: Request):
    pairs = parse_qsl((await req.body()).decode(), keep_blank_values=True); d = dict(pairs)
    s = "&".join(f"{k}={quote_plus(v)}" for k, v in pairs if k != "signature")
    if os.getenv("PAYFAST_PASSPHRASE"): s += f"&passphrase={quote_plus(os.environ['PAYFAST_PASSPHRASE'])}"
    ok = hmac.compare_digest(hashlib.md5(s.encode()).hexdigest(), d.get("signature", "")) and d.get("merchant_id") == os.getenv("PAYFAST_MERCHANT_ID")
    if not ok: raise HTTPException(400, "Bad signature")
    if d.get("payment_status") == "COMPLETE" and d.get("custom_str1") and d.get("amount_gross") in PRICE_TIER:
        store.set_tier(d["custom_str1"], PRICE_TIER[d["amount_gross"]])
    return "OK"

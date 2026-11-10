import hashlib, hmac, logging, os, time, uuid, datetime as dt
from collections import defaultdict, deque
from urllib.parse import parse_qsl, quote_plus
import httpx
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from . import engine, store

log = logging.getLogger("spazachef")
QUOTA = {"free": 5, "basic": 30, "premium": 10_000}
PLANS = {"basic": ("15.00", "SpazaChef Basic"), "premium": ("99.00", "SpazaChef Premium")}
PRICE_TIER = {v[0]: k for k, v in PLANS.items()}
app = FastAPI(title="SpazaChef API", docs_url=None if os.getenv("ENV") == "production" else "/docs", redoc_url=None)
app.add_middleware(CORSMiddleware, allow_origins=[o for o in os.getenv("ORIGINS", "http://localhost:5173").split(",") if o],
                   allow_methods=["GET", "POST"], allow_headers=["*"])
hits = defaultdict(deque)  # per-instance limiter; add an edge/WAF limit for hard guarantees
env = lambda k: os.environ.get(k, "")
pf_host = lambda: "sandbox.payfast.co.za" if env("PAYFAST_SANDBOX") == "1" else "www.payfast.co.za"

@app.exception_handler(httpx.HTTPError)
async def upstream(_, e):
    log.error("upstream error: %s", e)
    return JSONResponse({"detail": "Service temporarily unavailable. Try again shortly."}, status_code=503)

@app.middleware("http")
async def security_headers(req, call_next):
    r = await call_next(req); r.headers["X-Content-Type-Options"] = "nosniff"; r.headers["Cache-Control"] = "no-store"; return r

def who(req: Request, auth):
    ip = (req.headers.get("x-forwarded-for") or req.client.host).split(",")[0].strip()
    t = hits[ip]; now = time.time()
    while t and now - t[0] > 60: t.popleft()
    if len(t) >= 30: raise HTTPException(429, "Too many requests. Wait a minute and try again.")
    t.append(now)
    if auth:
        r = httpx.get(env("SUPABASE_URL").rstrip("/") + "/auth/v1/user",
                      headers={"apikey": env("SUPABASE_PUBLISHABLE_KEY"), "Authorization": auth}, timeout=5)
        if r.status_code != 200: raise HTTPException(401, "Your session expired. Sign in again.")
        uid = r.json()["id"]; return uid, store.tier(uid) or "free"
    return "ip:" + ip, "free"

class Brief(BaseModel):
    persona: str = "zanele"; ingredients: str = Field(min_length=2, max_length=2000)
    diet: str = Field("", max_length=60); serves: int = Field(4, ge=1, le=20); notes: str = Field("", max_length=200)
class Feedback(BaseModel):
    rating: int | None = Field(None, ge=1, le=5); cooked: bool = False; regenerated: bool = False

today = lambda: dt.date.today().isoformat()

@app.get("/api/health")
def health(): return {"ok": True}

@app.get("/api/me")
def me(req: Request, authorization: str | None = Header(None)):
    uid, t = who(req, authorization)
    return {"tier": t, "used": store.used(uid, today()), "limit": QUOTA[t], "signed_in": not uid.startswith("ip:")}

@app.post("/api/recipes/generate")
def generate(b: Brief, req: Request, authorization: str | None = Header(None)):
    uid, tier = who(req, authorization)
    try: r = engine.generate(b.model_dump(), b.persona, store.weights())
    except ValueError as e: raise HTTPException(422, str(e))
    if not store.use(uid, today(), QUOTA.get(tier, 5)): raise HTTPException(402, "You've used today's recipes. Upgrade for more.")
    store.add_recipe(uid, r); return r

@app.get("/api/recipes")
def mine(req: Request, authorization: str | None = Header(None)): return store.recipes(who(req, authorization)[0])

@app.post("/api/recipes/{rid}/feedback")
def feedback(rid: str, f: Feedback, req: Request, authorization: str | None = Header(None)):
    uid, _ = who(req, authorization); r = store.get(uid, rid)
    if not r: raise HTTPException(404, "Recipe not found.")
    store.mark(uid, rid, f.rating, f.cooked)
    store.save_weights(engine.learn(store.weights(), r["persona"], r["archetype"], f.rating, f.cooked, f.regenerated))
    return {"ok": True}

def pf_sig(pairs, skip_empty):
    s = "&".join(f"{k}={quote_plus(str(v).strip())}" for k, v in pairs if not (skip_empty and str(v).strip() == ""))
    if env("PAYFAST_PASSPHRASE"): s += f"&passphrase={quote_plus(env('PAYFAST_PASSPHRASE').strip())}"
    return hashlib.md5(s.encode()).hexdigest()

@app.get("/api/billing/checkout")
def checkout(tier: str, req: Request, authorization: str | None = Header(None)):
    uid, _ = who(req, authorization)
    if uid.startswith("ip:"): raise HTTPException(401, "Sign in to upgrade.")
    if tier not in PLANS: raise HTTPException(422, "Unknown plan.")
    amt, name = PLANS[tier]; fe = env("FRONTEND_URL").rstrip("/"); api = env("API_URL").rstrip("/")
    pairs = [("merchant_id", env("PAYFAST_MERCHANT_ID")), ("merchant_key", env("PAYFAST_MERCHANT_KEY")),
             ("return_url", fe + "/?paid=1"), ("cancel_url", fe + "/"), ("notify_url", api + "/api/payfast/itn"),
             ("m_payment_id", uuid.uuid4().hex), ("amount", amt), ("item_name", name), ("custom_str1", uid),
             ("subscription_type", "1"), ("recurring_amount", amt), ("frequency", "3"), ("cycles", "0")]
    return {"action": f"https://{pf_host()}/eng/process", "fields": dict(pairs) | {"signature": pf_sig(pairs, True)}}

@app.post("/api/payfast/itn")
async def itn(req: Request):
    raw = (await req.body()).decode()
    all_pairs = parse_qsl(raw, keep_blank_values=True)
    pairs = [(k, v) for k, v in all_pairs if k != "signature"]; d = dict(all_pairs)
    if not (hmac.compare_digest(pf_sig(pairs, False), d.get("signature", "")) and d.get("merchant_id") == env("PAYFAST_MERCHANT_ID")):
        raise HTTPException(400, "Bad signature")
    v = httpx.post(f"https://{pf_host()}/eng/query/validate", content="&".join(f"{k}={quote_plus(x)}" for k, x in pairs),
                   headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=10)
    if v.text.strip() != "VALID": raise HTTPException(400, "PayFast validation failed")
    uid = d.get("custom_str1", "")
    if uid and d.get("payment_status") == "COMPLETE" and d.get("amount_gross") in PRICE_TIER:
        store.set_tier(uid, PRICE_TIER[d["amount_gross"]])
    elif uid and d.get("payment_status") == "CANCELLED":
        store.set_tier(uid, "free")
    return "OK"

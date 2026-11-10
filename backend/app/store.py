"""Supabase (PostgREST) storage. Needs SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (server only)."""
import os
from urllib.parse import quote
import httpx
_c = None
MERGE = {"Prefer": "resolution=merge-duplicates,return=minimal"}
def _client():
    global _c
    if _c is None:
        k = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
        _c = httpx.Client(base_url=os.environ["SUPABASE_URL"].rstrip("/") + "/rest/v1", timeout=10,
                          headers={"apikey": k, "Authorization": "Bearer " + k, "Content-Type": "application/json"})
    return _c
def _r(method, path, **kw):
    r = _client().request(method, path, **kw); r.raise_for_status(); return r.json() if r.content else None
def weights(): return {x["k"]: (x["a"], x["b"]) for x in _r("GET", "/sc2_weights?select=*")}
def save_weights(w):
    if w: _r("POST", "/sc2_weights?on_conflict=k", json=[{"k": k, "a": a, "b": b} for k, (a, b) in w.items()], headers=MERGE)
def add_recipe(uid, r): _r("POST", "/sc2_recipes", json={"id": r["id"], "uid": uid, "body": r}, headers={"Prefer": "return=minimal"})
def recipes(uid, n=30):
    rows = _r("GET", f"/sc2_recipes?uid=eq.{quote(uid)}&order=created_at.desc&limit={n}&select=body,rating,cooked")
    return [x["body"] | {"rating": x["rating"], "cooked": x["cooked"]} for x in rows]
def get(uid, rid):
    rows = _r("GET", f"/sc2_recipes?id=eq.{quote(rid)}&uid=eq.{quote(uid)}&select=body"); return rows[0]["body"] if rows else None
def mark(uid, rid, rating, cooked):
    p = {**({"rating": rating} if rating is not None else {}), **({"cooked": True} if cooked else {})}
    if p: _r("PATCH", f"/sc2_recipes?id=eq.{quote(rid)}&uid=eq.{quote(uid)}", json=p, headers={"Prefer": "return=minimal"})
def used(uid, day):
    rows = _r("GET", f"/sc2_usage?uid=eq.{quote(uid)}&day=eq.{day}&select=n"); return rows[0]["n"] if rows else 0
def use(uid, day, limit):
    n = used(uid, day)
    if n >= limit: return False
    _r("POST", "/sc2_usage?on_conflict=uid,day", json={"uid": uid, "day": day, "n": n + 1}, headers=MERGE); return True
def tier(uid):
    rows = _r("GET", f"/sc2_tiers?uid=eq.{quote(uid)}&select=tier"); return rows[0]["tier"] if rows else None
def set_tier(uid, t): _r("POST", "/sc2_tiers?on_conflict=uid", json={"uid": uid, "tier": t}, headers=MERGE)

import json, os, sqlite3, threading
_L = threading.Lock(); PATH = os.getenv("DATABASE_PATH", "spazachef.db")
def db():
    c = sqlite3.connect(PATH, check_same_thread=False); c.row_factory = sqlite3.Row
    c.executescript("""create table if not exists recipes(id text primary key, uid text, body text, rating int, cooked int default 0, at text default current_timestamp);
    create table if not exists weights(k text primary key, a real, b real);
    create table if not exists usage(uid text, day text, n int, primary key(uid, day));
    create table if not exists tiers(uid text primary key, tier text);""")
    return c
def weights():
    with _L, db() as c: return {r["k"]: (r["a"], r["b"]) for r in c.execute("select * from weights")}
def save_weights(w):
    with _L, db() as c: c.executemany("insert into weights values(?,?,?) on conflict(k) do update set a=excluded.a,b=excluded.b", [(k, *v) for k, v in w.items()])
def add_recipe(uid, r):
    with _L, db() as c: c.execute("insert into recipes(id,uid,body) values(?,?,?)", (r["id"], uid, json.dumps(r)))
def recipes(uid, n=30):
    with _L, db() as c: return [json.loads(r["body"]) | {"rating": r["rating"], "cooked": bool(r["cooked"])} for r in c.execute("select * from recipes where uid=? order by at desc limit ?", (uid, n))]
def get(uid, rid):
    with _L, db() as c:
        r = c.execute("select * from recipes where id=? and uid=?", (rid, uid)).fetchone(); return r and json.loads(r["body"])
def mark(uid, rid, rating, cooked):
    with _L, db() as c: c.execute("update recipes set rating=coalesce(?,rating), cooked=max(cooked,?) where id=? and uid=?", (rating, int(cooked), rid, uid))
def use(uid, day, limit):
    with _L, db() as c:
        n = (c.execute("select n from usage where uid=? and day=?", (uid, day)).fetchone() or [0])[0]
        if n >= limit: return False
        c.execute("insert into usage values(?,?,1) on conflict(uid,day) do update set n=n+1", (uid, day)); return True
def tier(uid):
    with _L, db() as c: r = c.execute("select tier from tiers where uid=?", (uid,)).fetchone(); return r and r["tier"]
def set_tier(uid, t):
    with _L, db() as c: c.execute("insert into tiers values(?,?) on conflict(uid) do update set tier=excluded.tier", (uid, t))

"""SQLite persistence for the single-node deployment profile."""
import json
import os
import sqlite3
import threading
from contextlib import contextmanager

_LOCK = threading.RLock()
_PATH = os.getenv("DATABASE_PATH", "spazachef.db")


def _connect():
    parent = os.path.dirname(os.path.abspath(_PATH))
    os.makedirs(parent, exist_ok=True)
    connection = sqlite3.connect(_PATH, timeout=10, isolation_level="DEFERRED")
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout = 10000")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    connection.executescript("""
        CREATE TABLE IF NOT EXISTS recipes(
            id TEXT PRIMARY KEY, uid TEXT NOT NULL, body TEXT NOT NULL,
            rating INTEGER, cooked INTEGER NOT NULL DEFAULT 0,
            at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS recipes_uid_at ON recipes(uid, at DESC);
        CREATE TABLE IF NOT EXISTS weights(k TEXT PRIMARY KEY, a REAL NOT NULL, b REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS usage(uid TEXT NOT NULL, day TEXT NOT NULL, n INTEGER NOT NULL,
            PRIMARY KEY(uid, day));
        CREATE TABLE IF NOT EXISTS tiers(uid TEXT PRIMARY KEY, tier TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS payments(
            payment_id TEXT PRIMARY KEY, uid TEXT NOT NULL, tier TEXT NOT NULL,
            amount TEXT NOT NULL, at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS checkout_orders(
            order_id TEXT PRIMARY KEY, uid TEXT NOT NULL, tier TEXT NOT NULL,
            amount TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending',
            at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)
    return connection


@contextmanager
def db():
    connection = _connect()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize():
    with _LOCK, db():
        pass


def weights():
    with _LOCK, db() as connection:
        return {row["k"]: (row["a"], row["b"]) for row in connection.execute("SELECT * FROM weights")}


def save_weights(values):
    with _LOCK, db() as connection:
        connection.executemany(
            "INSERT INTO weights VALUES(?,?,?) ON CONFLICT(k) DO UPDATE SET a=excluded.a,b=excluded.b",
            [(key, *value) for key, value in values.items()],
        )


def add_recipe(uid, recipe):
    with _LOCK, db() as connection:
        connection.execute("INSERT INTO recipes(id,uid,body) VALUES(?,?,?)", (recipe["id"], uid, json.dumps(recipe)))


def recipes(uid, n=30):
    with _LOCK, db() as connection:
        rows = connection.execute(
            "SELECT body,rating,cooked FROM recipes WHERE uid=? ORDER BY at DESC LIMIT ?", (uid, n)
        )
        return [json.loads(row["body"]) | {"rating": row["rating"], "cooked": bool(row["cooked"])} for row in rows]


def get(uid, rid):
    with _LOCK, db() as connection:
        row = connection.execute("SELECT body FROM recipes WHERE id=? AND uid=?", (rid, uid)).fetchone()
        return row and json.loads(row["body"])


def mark(uid, rid, rating, cooked):
    with _LOCK, db() as connection:
        connection.execute(
            "UPDATE recipes SET rating=coalesce(?,rating), cooked=max(cooked,?) WHERE id=? AND uid=?",
            (rating, int(cooked), rid, uid),
        )


def use(uid, day, limit):
    with _LOCK, db() as connection:
        row = connection.execute(
            "INSERT INTO usage(uid,day,n) VALUES(?,?,1) "
            "ON CONFLICT(uid,day) DO UPDATE SET n=n+1 WHERE usage.n < ? RETURNING n",
            (uid, day, limit),
        ).fetchone()
        return row is not None


def tier(uid):
    with _LOCK, db() as connection:
        row = connection.execute("SELECT tier FROM tiers WHERE uid=?", (uid,)).fetchone()
        return row and row["tier"]


def create_checkout_order(order_id, uid, tier_name, amount):
    with _LOCK, db() as connection:
        connection.execute(
            "INSERT INTO checkout_orders(order_id,uid,tier,amount) VALUES(?,?,?,?)",
            (order_id, uid, tier_name, amount),
        )


def record_payment(payment_id, order_id, uid, tier_name, amount):
    """Apply a verified ITN only to its matching server-created order."""
    with _LOCK, db() as connection:
        order = connection.execute(
            "SELECT uid,tier,amount,status FROM checkout_orders WHERE order_id=?", (order_id,)
        ).fetchone()
        if not order or (order["uid"], order["tier"], order["amount"]) != (uid, tier_name, amount):
            return False
        if order["status"] == "paid":
            return connection.execute(
                "SELECT 1 FROM payments WHERE payment_id=? AND uid=? AND tier=? AND amount=?",
                (payment_id, uid, tier_name, amount),
            ).fetchone() is not None
        cursor = connection.execute(
            "INSERT OR IGNORE INTO payments(payment_id,uid,tier,amount) VALUES(?,?,?,?)",
            (payment_id, uid, tier_name, amount),
        )
        if not cursor.rowcount:
            return False
        connection.execute(
            "INSERT INTO tiers(uid,tier) VALUES(?,?) "
            "ON CONFLICT(uid) DO UPDATE SET tier=excluded.tier", (uid, tier_name)
        )
        connection.execute("UPDATE checkout_orders SET status='paid' WHERE order_id=?", (order_id,))
        return True


import json
import os

import psycopg
from psycopg.rows import dict_row


def db():
    """Open a short-lived SSL Postgres connection; use Supavisor session pooling for persistent APIs."""
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("DATABASE_URL is required; SQLite is not supported in production.")
    return psycopg.connect(
        url,
        connect_timeout=5,
        sslmode="require",
        row_factory=dict_row,
        prepare_threshold=None,
        application_name="spazachef-api",
    )


def weights():
    with db() as conn:
        rows = conn.execute("select k, a, b from public.weights").fetchall()
        return {row["k"]: (row["a"], row["b"]) for row in rows}


def save_weights(values):
    if not values:
        return
    with db() as conn:
        conn.executemany(
            """insert into public.weights (k, a, b) values (%s, %s, %s)
               on conflict (k) do update set a = excluded.a, b = excluded.b""",
            [(key, *value) for key, value in values.items()],
        )


def add_recipe(uid, recipe):
    with db() as conn:
        conn.execute(
            "insert into public.recipes (id, uid, body) values (%s, %s, %s::jsonb)",
            (recipe["id"], uid, json.dumps(recipe)),
        )


def recipes(uid, n=30):
    with db() as conn:
        rows = conn.execute(
            """select body, rating, cooked from public.recipes
               where uid = %s order by created_at desc limit %s""",
            (uid, n),
        ).fetchall()
        return [
            row["body"] | {"rating": row["rating"], "cooked": row["cooked"]}
            for row in rows
        ]


def get(uid, recipe_id):
    with db() as conn:
        row = conn.execute(
            "select body from public.recipes where id = %s and uid = %s",
            (recipe_id, uid),
        ).fetchone()
        return row and row["body"]


def mark(uid, recipe_id, rating, cooked):
    with db() as conn:
        conn.execute(
            """update public.recipes
               set rating = coalesce(%s, rating), cooked = cooked or %s
               where id = %s and uid = %s""",
            (rating, bool(cooked), recipe_id, uid),
        )


def use(uid, day, limit):
    """Atomically consume one daily allowance across all API workers."""
    with db() as conn:
        row = conn.execute(
            """insert into public.usage (uid, day, n) values (%s, %s, 1)
               on conflict (uid, day) do update
                 set n = public.usage.n + 1
                 where public.usage.n < %s
               returning n""",
            (uid, day, limit),
        ).fetchone()
        return row is not None


def tier(uid):
    with db() as conn:
        row = conn.execute(
            "select tier from public.tiers where uid = %s",
            (uid,),
        ).fetchone()
        return row and row["tier"]


def set_tier(uid, value):
    with db() as conn:
        conn.execute(
            """insert into public.tiers (uid, tier) values (%s, %s)
               on conflict (uid) do update set tier = excluded.tier""",
            (uid, value),
        )

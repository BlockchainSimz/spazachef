-- Apply this migration to the active SpazaChef PostgreSQL database before deploying
-- the API revision that uses store.allow_request().
create table if not exists public.api_rate_limits (
    uid text not null,
    route text not null,
    window_start bigint not null,
    n integer not null default 0 check (n >= 0),
    primary key (uid, route, window_start)
);
create index if not exists api_rate_limits_window_idx
    on public.api_rate_limits (window_start);
revoke all on table public.api_rate_limits from anon, authenticated;

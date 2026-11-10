create table if not exists public.sc2_recipes(id text primary key, uid text not null, body jsonb not null, rating int, cooked boolean not null default false, created_at timestamptz not null default now());
create index if not exists sc2_recipes_uid_created on public.sc2_recipes(uid, created_at desc);
create table if not exists public.sc2_weights(k text primary key, a double precision not null, b double precision not null);
create table if not exists public.sc2_usage(uid text not null, day date not null, n int not null default 0, primary key(uid, day));
create table if not exists public.sc2_tiers(uid text primary key, tier text not null check (tier in ('free','basic','premium')), updated_at timestamptz not null default now());
alter table public.sc2_recipes enable row level security;
alter table public.sc2_weights enable row level security;
alter table public.sc2_usage enable row level security;
alter table public.sc2_tiers enable row level security;

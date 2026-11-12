# SpazaChef v2 — isolated source import and hardening

This directory contains the React/Vite PWA + FastAPI recipe application, staged separately from the repository's existing application. The existing `main` branch has not been overwritten.

## Layout
- `frontend/`: React + Vite PWA with Supabase email/password sign-up, sign-in, session restoration, password recovery, and sign-out.
- `backend/app/engine.py`: local recipe composer and feedback-learning engine.
- `backend/app/store.py`: Supabase Postgres persistence for recipes, usage, tiers, and learning weights. Daily quota consumption is atomic across API workers.
- `backend/app/main.py`: validates ES256/RS256 access tokens through project JWKS and legacy HS256 tokens through the Supabase Auth `/user` endpoint.
- `backend/tests/`: recipe-engine and auth/payment regression tests.
- `PRODUCTION_READINESS_AUDIT.md`: engineering findings and release gates.

## Local development

Backend:
```bash
cd backend
python -m pip install -r requirements.txt
PYTHONPATH=. pytest -q
uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

### Frontend environment
- `VITE_SUPABASE_URL`: Supabase project URL.
- `VITE_SUPABASE_PUBLISHABLE_KEY`: publishable key only; safe for browser use.
- `VITE_API_URL`: API origin; leave empty when using the Vite `/api` development proxy.

### Backend environment
- `SUPABASE_URL`: Supabase project URL.
- `SUPABASE_PUBLISHABLE_KEY`: publishable key used when validating legacy HS256 sessions with Supabase Auth.
- `DATABASE_URL`: privileged Postgres connection string from Supabase **Connect**. Keep this server-side secret; never prefix it with `VITE_`. Use a suitable Supavisor connection mode for the chosen host.
- `ORIGINS`: comma-separated exact frontend origins.

The backend uses SSL for Postgres connections and disables prepared statements for compatibility with transaction poolers. SQLite is no longer used.

## Database
The active Supabase project has the following tables:
- `public.recipes`: user-owned recipe JSON, ratings, and cooked status.
- `public.usage`: per-user, per-day recipe counts.
- `public.tiers`: server-managed subscription tier.
- `public.weights`: global recipe-learning weights, private to the backend.

RLS is enabled on all four tables. Recipe and account rows have user-ownership policies; global weights have a deny-all authenticated policy. API operations use a privileged backend-only database connection and always scope user records by the verified Supabase user ID. Daily quota use is an atomic Postgres upsert.

The schema is applied to the connected Supabase project. The tables are currently empty; no legacy SQLite data has been imported.

## Security and payment status
- Missing Supabase auth configuration fails closed.
- ES256/RS256 tokens are verified against project JWKS, issuer, and audience.
- HS256 tokens are verified by Supabase Auth `/auth/v1/user`; the backend does not keep or expose the legacy JWT signing secret.
- Database outages return service-unavailable responses rather than being misreported as invalid credentials.
- Unknown tiers fall back to free.
- PayFast ITN remains disabled until provider-source verification, pending-order reconciliation, amount/currency checks, ownership checks, idempotency, and audit records are implemented.

## Remaining production blockers
- Set the actual backend `DATABASE_URL` secret and verify connectivity from the deployment runtime.
- Complete a live signup/login/session refresh/password recovery/API smoke test.
- Regenerate and commit the frontend lockfile; verify frontend production build and GitHub Actions.
- Configure and deploy the frontend and FastAPI backend; no Vercel project is currently linked to this isolated app.
- Add shared rate limiting, structured logs, monitoring, alerts, backup/restore tests, retention/deletion workflows, and rollback procedures.
- Harden dietary/allergen matching and food-safety guidance.
- Existing SQLite data has not been migrated; import only if it contains data that must be retained.

## Release decision
**Not production ready.** This is an isolated staging branch, not a deployable release. Do not enable payments or merge into the existing application until the remaining blockers and tests are resolved.


## Production hardening migration

Before deploying the API revision that uses shared rate limiting, apply
backend/migrations/002_api_rate_limits.sql to the active Supabase PostgreSQL
database using the Supabase SQL Editor or the project's migration workflow.
The migration creates a private, RLS-enabled rate-limit table. Do not grant
anon or authenticated access to it.

The backend now isolates recipe-learning weights by authenticated user.
Existing legacy global weights are not used by the new user-scoped lookup.

For production Vercel configuration, set:
- Frontend: VITE_SUPABASE_URL, VITE_SUPABASE_PUBLISHABLE_KEY
- Backend: SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, DATABASE_URL, ORIGINS, ENV=production

Never place a Supabase secret/service-role key in a VITE_ variable.

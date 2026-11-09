# SpazaChef v2 — isolated source import and hardening

This directory contains the uploaded React/Vite PWA + FastAPI recipe application, staged separately from the repository's existing application. The existing `main` branch has not been overwritten.

## Layout
- `frontend/`: React 18 + Vite PWA with Supabase email/password sign-up, sign-in, session restoration, automatic token refresh, password reset, and sign-out.
- `backend/app/engine.py`: local recipe composer and feedback-learning engine.
- `backend/app/store.py`: SQLite persistence for recipes, usage, tiers, and learning weights.
- `backend/app/main.py`: API entrypoint that validates Supabase JWTs using project JWKS (ES256/RS256) or a legacy HS256 JWT secret.
- `backend/tests/`: recipe-engine tests and authentication/payment security regression tests.
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
Configure the frontend build-time variables:
- `VITE_SUPABASE_URL`: Supabase project URL.
- `VITE_SUPABASE_PUBLISHABLE_KEY`: Supabase publishable key (safe for browser use; never use a secret/service-role key).
- `VITE_API_URL`: API origin; leave empty when using the Vite `/api` development proxy.

Configure the backend:
- `SUPABASE_URL`: same project URL; used to validate issuer and retrieve public signing keys from the project's JWKS endpoint.
- `SUPABASE_JWT_SECRET`: only needed for legacy HS256-signed access tokens.
- `ORIGINS`: comma-separated exact frontend origins.

## Security and payment status
- Authentication fails closed when no verifier is configured; missing/invalid Bearer tokens are rejected.
- The browser uses the Supabase SDK session store and access token; it does not manually copy tokens into an unrelated localStorage key.
- User-specific recent-recipe cache is namespaced by Supabase user ID.
- Unknown subscription tiers fall back to free.
- Invalid recipe generation is validated before daily quota consumption.
- PayFast ITN cannot grant paid tiers until provider source validation, server-side order matching, amount/currency verification, transaction idempotency, and audit logging are implemented.

## Known production blockers
- SQLite and process-local locking are not suitable for horizontally scaled production quota enforcement; migrate recipes, tiers, usage, and weights to managed Postgres with transactions and migrations.
- Shared rate limiting is still absent.
- Dietary/allergen matching and food-safety instructions need additional hardening.
- Configure environment variables in the actual frontend/backend deployment environments and complete an end-to-end Supabase signup/login/API test. No production Vercel project is currently linked to this isolated directory.
- Frontend lockfile still needs regeneration and commit after adding the Supabase SDK dependency; CI currently uses `npm install` until that lockfile is restored.
- No live PayFast, backup/restore, monitoring, or production deployment verification has been performed.

## Release decision
**Not production ready.** Treat this branch as an isolated staging/import PR, not a deployable release. Do not enable payments or merge into the existing application until the blockers and tests are resolved.

# SpazaChef v2 — isolated source import and hardening

This directory contains the uploaded React/Vite PWA + FastAPI recipe application, staged separately from the repository's existing application. The existing `main` branch has not been overwritten.

## Layout
- `frontend/`: React 18 + Vite single-page PWA.
- `backend/app/engine.py`: local recipe composer and feedback-learning engine.
- `backend/app/store.py`: SQLite persistence for recipes, usage, tiers, and learning weights.
- `backend/app/main.py`: hardened API entrypoint.
- `backend/tests/`: recipe-engine tests and security regression tests.
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
The frontend expects `VITE_API_URL` at build time (leave empty for the Vite `/api` development proxy). The backend requires `SUPABASE_JWT_SECRET` and a valid Supabase Bearer JWT for protected endpoints. Configure `ORIGINS` to the exact frontend origin(s).

## Security and payment status
- Authentication now fails closed: missing JWT configuration returns 503 and missing/invalid Bearer tokens return 401.
- Unknown subscription tiers fall back to free.
- Recipe generation is validated before quota consumption.
- PayFast ITN intentionally cannot grant paid tiers. It remains disabled until provider source validation, server-side order matching, amount/currency verification, transaction idempotency, and audit logging are implemented.

## Known production blockers
- SQLite and process-local locking are not suitable for horizontally scaled production quota enforcement; migrate to a managed transactional database and shared rate limiter.
- Frontend authentication UI/session integration is not implemented in this snapshot. The current frontend expects a token in localStorage, so users cannot sign in through this UI yet.
- The original `package-lock.json` was not imported into this branch; regenerate and commit it with `npm install` in a network-enabled environment, then run the production build.
- No live Supabase, PayFast, production deployment, backup/restore, or monitoring verification has been performed.
- Recipe dietary/allergen matching and food-safety instructions need additional hardening.

## Release decision
**Not production ready.** Treat this branch as an isolated staging/import PR, not a deployable release. Do not enable payments or merge into the existing application until the blockers and tests are resolved.

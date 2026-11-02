# SpazaChef v2

SpazaChef is a React/Vite installable web app with a FastAPI backend. The recipe engine is self-contained and does not send pantry data to an LLM or external recipe source.

## Run locally

1. Backend: `cd backend`, create a virtual environment, install `requirements.txt`, then run `uvicorn app.main:app --reload`.
2. Frontend: `cd frontend`, run `npm ci`, then `npm run dev`.
3. The Vite development server proxies `/api` to `http://localhost:8000`.

## Production configuration

Copy `.env.example` into the backend deployment environment and set real values. Production startup intentionally fails unless `SUPABASE_JWT_SECRET`, `SUPABASE_JWT_ISSUER`, `DATABASE_PATH`, and an HTTPS `ORIGINS` value are configured. Set `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` in the frontend build environment; these public values enable the built-in Supabase email/password sign-in form. The frontend sends the access token as a bearer token and refreshes it when needed. Use a dedicated Supabase project and its legacy HS256 JWT secret; rotate it if it has ever been exposed.

For Vercel, set the project root to `frontend/` and configure `VITE_API_URL`, `VITE_SUPABASE_URL`, and `VITE_SUPABASE_ANON_KEY` as build variables. The FastAPI image is built with `docker build -f backend/Dockerfile -t spazachef-api backend`. For a persistent single-node container, copy the backend settings to an untracked `.env.backend` file and run `docker compose up -d` from this directory; the Compose service mounts the `spazachef-data` volume at `/data`.

Use a persistent mounted volume for the absolute `DATABASE_PATH`. This SQLite deployment profile is for one backend instance on a durable local volume. Do not scale it across ephemeral or multi-region instances; use managed Postgres and a migration/repository layer for that deployment model. Back up the database and test restores before launch.

The authenticated `POST /api/payfast/checkout` endpoint creates a pending order and returns a server-signed PayFast form for the selected tier; the UI posts those fields directly to PayFast. Configure the merchant ID, merchant key, passphrase, and HTTPS return/cancel/notify URLs. ITN tier grants require a valid signature, matching merchant and server-verified payment, and a pending server-created order with the expected amount, user, and tier. Duplicate notifications are idempotent. Use `PAYFAST_SANDBOX=true` only with sandbox credentials. The current Basic and Premium amounts are one-time payments, and tiers remain active indefinitely; implement expiry or recurring billing before advertising time-limited subscriptions.

Place the API behind HTTPS and a gateway with request-size limits, abuse controls, and monitoring. Configure CORS to the exact frontend origin. Health checks are unauthenticated and return no deployment secrets.

## Build and checks

- Frontend production build: `cd frontend && npm ci && npm run build`
- Backend tests: `cd backend && pip install -r requirements-dev.txt && pytest`

The code paths are in place, but a live launch still requires real provider credentials, durable storage and tested backups, monitoring, and deployment-specific request limits. Verify Supabase email confirmation and PayFast sandbox end to end before switching to live merchant credentials.


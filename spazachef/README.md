# SpazaChef v2

SpazaChef is a React/Vite installable web app with a FastAPI backend. The recipe engine is self-contained and does not send pantry data to an LLM or external recipe source.

## Run locally

1. Backend: `cd backend`, create a virtual environment, install `requirements.txt`, then run `uvicorn app.main:app --reload`.
2. Frontend: `cd frontend`, run `npm ci`, then `npm run dev`.
3. The Vite development server proxies `/api` to `http://localhost:8000`.

## Production configuration

Copy `.env.example` into the backend deployment environment and set real values. Production startup intentionally fails unless `SUPABASE_JWT_SECRET`, `SUPABASE_JWT_ISSUER`, `DATABASE_PATH`, and an HTTPS `ORIGINS` value are configured. Set `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` in the frontend build environment; these public values enable the built-in Supabase email/password sign-in form. The frontend sends the access token as a bearer token and refreshes it when needed. Use a dedicated Supabase project and its legacy HS256 JWT secret; rotate it if it has ever been exposed.

Use a persistent mounted volume for the absolute `DATABASE_PATH`. This SQLite deployment profile is for one backend instance on a durable local volume. Do not scale it across ephemeral or multi-region instances; use managed Postgres and a migration/repository layer for that deployment model. Back up the database and test restores before launch.

PayFast plans are granted only after the ITN signature, merchant, amount, server validation, and unique payment ID are checked. Configure the exact merchant ID and passphrase on the backend. Use `PAYFAST_SANDBOX=true` only with sandbox credentials. The UI still needs an authenticated checkout flow that creates the signed PayFast payment request; do not grant tiers from client input.

Place the API behind HTTPS and a gateway with request-size limits, abuse controls, and monitoring. Configure CORS to the exact frontend origin. Health checks are unauthenticated and return no deployment secrets.

## Build and checks

- Frontend production build: `cd frontend && npm ci && npm run build`
- Backend tests: `cd backend && pytest`

The app is not launch-ready until production secrets, Supabase auth integration, PayFast checkout creation, persistent storage/backup, monitoring, and deployment-specific abuse controls are configured and exercised.


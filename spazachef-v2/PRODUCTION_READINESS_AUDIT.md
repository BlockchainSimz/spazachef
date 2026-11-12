# SpazaChef v2 — Production Readiness Audit

**Audit date:** 2026-11-09  
**Artifact reviewed:** uploaded `spazachef-v2.zip`  
**Decision:** **NOT PRODUCTION READY — prototype / pre-production**

## Verification performed
- Vercel frontend preview build completed successfully for the hardening branch.
- Vercel FastAPI preview build completed successfully for the hardening branch.
- Both Vercel checks reported success for the preview commit; this verifies builds, not live API/database behaviour.
- The active Supabase project is `itkovoagalodjqfjvmlp` (SpazaChef, eu-west-1); its four application tables have RLS enabled.
- Applied the `api_rate_limits` migration successfully and verified the new table exists with RLS enabled.
- Configured Vercel frontend Supabase URL/publishable key and environment-specific API URLs (production API for production, branch API for this preview, localhost for development); backend Supabase URL/publishable key/CORS/ENV variables are set.
- Vercel has a sensitive `DATABASE_URL` variable for Preview and Production, but the live readiness probe fails because its value is an HTTPS Supabase project URL rather than a PostgreSQL connection URI. Replace it with the exact Supabase Transaction Pooler URI from the project Connect dialog.
- GitHub Actions run #33 completed successfully: frontend TypeScript/Vite build passed and backend suite passed 14 tests. One Starlette/AnyIO deprecation warning remains.
- The latest frontend and backend Vercel preview deployments are both READY for commit 8dceff9. They are preview deployments, not production releases.
- Browser-based signup/login/recovery and live protected recipe API calls have not yet been exercised.
- Live PayFast callbacks, production backups, monitoring, and restore drills remain unverified.

## Implemented in this staging patch
1. **Fail-closed authentication:** API requires a Bearer JWT and returns 503 when Supabase verification configuration is missing.
2. **Supabase signing-key compatibility:** asymmetric ES256/RS256 access tokens are verified with the project's public JWKS, expected issuer, and authenticated audience. HS256 tokens are validated by calling the project's Auth `/auth/v1/user` endpoint with the publishable key; the backend does not store the legacy signing secret.
3. **Customer auth flow:** React UI includes email/password sign-up, sign-in, session restoration, automatic refresh, password reset email, password update after recovery, and sign-out.
4. **Session handling:** API requests use the Supabase SDK's current access token; recent recipe cache is isolated by user ID.
5. **Payment protection:** PayFast ITN cannot grant paid tiers while provider validation and order reconciliation are missing.
6. **Quota sequencing:** recipe generation is validated before daily quota consumption.
7. **CI:** adds frontend build and backend test jobs for changes under `spazachef-v2/`.

## Follow-up hardening added on 2026-11-12 (staging branch)
1. Added PostgreSQL-backed per-user/per-route fixed-window rate limiting for recipe generation, recipe listing, and feedback. Its migration has now been applied to the active SpazaChef database.
2. Isolated recipe-learning weights by authenticated user while retaining the existing weights table shape.
3. Added database/auth readiness at /api/ready, kept /api/health as liveness, and disabled production API docs by default.
4. Added regression tests for rate limiting, database readiness failure, fish exclusion from vegetarian recipes, and dairy/egg exclusion from vegan recipes.
5. Corrected Vercel service configuration with the FastAPI entrypoint and SPA deep-link fallback.

These changes are committed to codex/production-hardening-20261112. Vercel preview builds and GitHub CI are green; live production smoke tests remain pending.

## Remaining critical/high-priority blockers
1. **Backend database connection is misconfigured.** The Vercel `DATABASE_URL` secret currently contains the Supabase HTTPS API URL; Psycopg reports `missing '=' after 'https://itkovoagalodjqfjvmlp.supabase.co' in connection info string`. Replace it with the exact Transaction Pooler URI from Supabase Dashboard → Connect → Transaction pooler, with the database password URL-encoded. Keep it sensitive and never expose it to the browser.
2. **CI and full regression tests are pending.** The Vercel frontend and backend preview builds passed; wait for the GitHub Actions test workflow and fix any failures before merge.
3. **End-to-end auth verification is pending.** Test sign-up, email confirmation, login, refresh, logout, password recovery, and protected recipe API calls against the active SpazaChef Supabase project after DATABASE_URL is configured.
4. **Database connection is not verified from the API runtime.** The backend uses Psycopg over SSL and expects a PostgreSQL URI, not the Supabase HTTPS project URL. Use the exact shared Transaction Pooler connection string copied from the Supabase Connect dialog (host and pooler index must not be guessed). The database schema and row ownership policies were inspected; four application tables have user-scoped policies and weights are backend-only. Daily usage is now consumed with one atomic Postgres upsert, avoiding the old process-local quota race. Existing SQLite data has not been imported; the active Supabase tables are currently empty. Hosted schema verification confirmed the four application tables have RLS enabled; the rate-limit table is also RLS-enabled with no anon/authenticated grants. Existing sc2_* tables have INFO-level advisor notices because they have RLS enabled without policies.
5. **Shared rate limiting is implemented.** Verify live enforcement after DATABASE_URL is configured and monitor rate-limit table retention.
6. **PayFast is intentionally disabled.** Implement provider-source verification, server-side pending orders, amount/currency matching, ownership, unique transaction IDs, replay protection/idempotency, and audit records before re-enabling.
7. **Dietary and food safety controls are incomplete.** Filtering is substring-based and may misclassify ingredients; allergen handling and safe internal-temperature guidance are absent.
8. **Operational readiness is unverified.** Add health/readiness checks, structured logs, monitoring/alerts, database backup/restore tests, retention/deletion workflows, and deployment rollback procedures.

## Repository and release note
The uploaded v2 application differs from the repository's existing `main` application. This source import is intentionally isolated under `spazachef-v2/` on a draft branch; it must not replace the existing app. No production deployment has been performed.

**Release recommendation:** Do not deploy this branch as production, do not enable paid subscriptions, and do not merge until the remaining blockers are resolved and verified.


## Live API smoke test — 2026-11-12
- Frontend preview HTML and JS bundle return HTTP 200; the built bundle contains the expected branch API base URL.
- API preview `/api/health` returns HTTP 200.
- API preview `/api/recipes/generate` returns HTTP 405 to GET, confirming the route is registered and correctly requires POST.
- API preview `/api/ready` returns HTTP 503. Runtime logs identify the cause: `DATABASE_URL` is an HTTPS Supabase project URL, not a PostgreSQL URI.
- The API preview alias has a scoped Vercel protection override for testing; revoke it after preview verification.
- No production deployment or merge to `main` has been performed. PR #3 still targets the isolated V2 staging branch.


## Isolated API preview infrastructure
- A separate Git-linked Vercel project, `spazachef-api-v2`, is configured with root directory `spazachef-v2/backend` and public API access; the FastAPI layer continues to require Supabase JWTs for user data routes.
- The original `spazachef-api` project root directory and preview setting were restored to avoid changing the existing API project's deployment path while V2 is validated.
- The isolated V2 API preview still requires its own sensitive PostgreSQL `DATABASE_URL` before readiness can pass.

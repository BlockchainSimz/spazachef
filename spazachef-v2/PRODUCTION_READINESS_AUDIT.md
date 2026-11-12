# SpazaChef v2 — Production Readiness Audit

**Audit date:** 2026-11-09  
**Artifact reviewed:** uploaded `spazachef-v2.zip`  
**Decision:** **NOT PRODUCTION READY — prototype / pre-production**

## Verification performed
- Initial backend suite: 3 passed.
- Earlier backend snapshot: 9 tests passed locally. The current Postgres/auth refactor adds/changes regression tests and has **not yet been rerun** because the local environment cannot download the pinned psycopg driver; no GitHub Actions run has been returned.
- Frontend production build remains unverified; GitHub Actions workflow was added, but no workflow run was returned by the status lookup.
- Frontend build: not yet verified after adding the Supabase SDK and auth screens.
- Live Supabase signup, confirmation email, password reset, browser session refresh, and API JWT verification: not yet exercised end-to-end.
- Live PayFast callbacks, production database, backups, monitoring, and deployment: not verified.

## Implemented in this staging patch
1. **Fail-closed authentication:** API requires a Bearer JWT and returns 503 when Supabase verification configuration is missing.
2. **Supabase signing-key compatibility:** asymmetric ES256/RS256 access tokens are verified with the project's public JWKS, expected issuer, and authenticated audience. HS256 tokens are validated by calling the project's Auth `/auth/v1/user` endpoint with the publishable key; the backend does not store the legacy signing secret.
3. **Customer auth flow:** React UI includes email/password sign-up, sign-in, session restoration, automatic refresh, password reset email, password update after recovery, and sign-out.
4. **Session handling:** API requests use the Supabase SDK's current access token; recent recipe cache is isolated by user ID.
5. **Payment protection:** PayFast ITN cannot grant paid tiers while provider validation and order reconciliation are missing.
6. **Quota sequencing:** recipe generation is validated before daily quota consumption.
7. **CI:** adds frontend build and backend test jobs for changes under `spazachef-v2/`.

## Follow-up hardening added on 2026-11-12 (staging branch)
1. Added PostgreSQL-backed per-user/per-route fixed-window rate limiting for recipe generation, recipe listing, and feedback. The new migration must be applied before deploying this API revision.
2. Isolated recipe-learning weights by authenticated user while retaining the existing weights table shape.
3. Added database/auth readiness at /api/ready, kept /api/health as liveness, and disabled production API docs by default.
4. Added regression tests for rate limiting, database readiness failure, fish exclusion from vegetarian recipes, and dairy/egg exclusion from vegan recipes.
5. Corrected Vercel service configuration with the FastAPI entrypoint and SPA deep-link fallback.

These changes are committed to codex/production-hardening-20261112. They are not yet proven by a completed CI run or live production smoke test.

## Remaining critical/high-priority blockers
1. **Deployment environment is not configured.** Set `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY`, `VITE_API_URL` for the frontend and `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, `ORIGINS`, and storage settings for the backend. Never expose a Supabase secret/service-role key to the browser.
2. **Frontend build and CI are pending.** The lockfile must be regenerated after the new SDK dependency is added; CI currently uses npm install rather than npm ci.
3. **End-to-end auth verification is pending.** Test sign-up, email confirmation, login, refresh, logout, password recovery, and protected recipe API calls against the active SpazaChef Supabase project.
4. **Database connection is not configured or verified from the API runtime.** The backend now requires a privileged `DATABASE_URL` secret (never a `VITE_` variable) and uses psycopg over SSL. Configure it with the Supabase connection string and a suitable Supavisor pooler mode. Daily usage is now consumed with one atomic Postgres upsert, avoiding the old process-local quota race. Existing SQLite data has not been imported; the active Supabase tables are currently empty. Hosted schema verification confirmed four tables, RLS enabled on all four, seven policies, and no anon/authenticated table SELECT grants.
5. **Shared rate limiting is absent.** Implement a shared limiter using a trusted proxy or managed store.
6. **PayFast is intentionally disabled.** Implement provider-source verification, server-side pending orders, amount/currency matching, ownership, unique transaction IDs, replay protection/idempotency, and audit records before re-enabling.
7. **Dietary and food safety controls are incomplete.** Filtering is substring-based and may misclassify ingredients; allergen handling and safe internal-temperature guidance are absent.
8. **Operational readiness is unverified.** Add health/readiness checks, structured logs, monitoring/alerts, database backup/restore tests, retention/deletion workflows, and deployment rollback procedures.

## Repository and release note
The uploaded v2 application differs from the repository's existing `main` application. This source import is intentionally isolated under `spazachef-v2/` on a draft branch; it must not replace the existing app. No production deployment has been performed.

**Release recommendation:** Do not deploy this branch as production, do not enable paid subscriptions, and do not merge until the remaining blockers are resolved and verified.

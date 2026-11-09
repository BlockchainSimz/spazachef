# SpazaChef v2 — Production Readiness Audit

**Audit date:** 2026-11-09  
**Artifact reviewed:** `spazachef-v2.zip`  
**Snapshot commit:** `288128d`  
**Decision:** **NOT PRODUCTION READY — prototype / pre-production**

## Verification performed

- Backend unit tests: **3 passed** (`pytest -q`).
- Frontend production build: **not verified**; `npm ci` did not complete within the available execution window, so `npm run build` was not reached.
- Live deployment, database persistence, authentication-provider integration, payment-provider callbacks, backups, and production monitoring: **not verified**.

## Critical blockers

1. **Authentication is fail-open.** If `SUPABASE_JWT_SECRET` is absent, requests are assigned an IP-based identity and allowed through as a free user. This is not an acceptable production authentication boundary.
2. **Client-controlled identity boundary.** `X-Forwarded-For` is trusted directly for identity/rate limiting. Unless the proxy chain is configured and validated, clients can spoof it and bypass per-IP limits.
3. **Payment notification validation is incomplete.** The PayFast ITN handler checks a locally computed signature and merchant ID, but does not verify the provider source, amount/currency against a server-side order, transaction uniqueness, or a pending order belonging to the authenticated user. A signed but replayed or mismatched notification could grant entitlements.
4. **Quota consumption is not atomic with successful generation.** Usage is incremented before generation; invalid requests can consume quota. In-process locking and SQLite do not provide safe multi-instance quota enforcement.
5. **Persistence architecture is single-node SQLite.** The deployment notes require a persistent volume. There are no migrations, backup/restore automation, multi-instance coordination, or demonstrated durability checks.
6. **No API integration/security tests.** Existing tests cover only recipe-engine behavior; there are no tests for auth enforcement, quotas, ownership, rate limiting, CORS, or PayFast ITN.
7. **Recipe safety and dietary constraints are under-specified.** Cooking instructions use generic times and omit internal-temperature guidance for meat; dietary filtering only recognizes a `veg` substring and does not reliably enforce allergens or other dietary requirements.

## High-priority improvements

- Require valid Supabase JWTs in production; fail startup when required secrets are absent.
- Use verified proxy configuration and a shared rate limiter.
- Implement PayFast ITN verification per current provider guidance, including source verification, amount/currency/order matching, idempotency, and transaction audit records.
- Move usage, tiers, recipes, and learning weights to a production database with migrations and transactional quota enforcement.
- Add endpoint-level tests and CI for backend and frontend; complete the frontend build in a clean environment.
- Add privacy notice, retention/deletion workflows, operational logging, metrics, backups, and incident procedures before making POPIA compliance claims.
- Add food-safety instructions and explicit dietary/allergen validation.

## Scope and repository note

The uploaded archive is a self-contained React/Vite + FastAPI + SQLite implementation with snapshot commit `288128d`. The existing GitHub repository's `main` branch is a different, larger SpazaChef application (React 19/API router architecture), not the same source tree. The v2 snapshot must therefore be imported on an isolated branch/subdirectory and reviewed before any merge or deployment; replacing the existing `main` tree would be destructive.

**Release recommendation:** Do not deploy this snapshot to production or enable paid subscriptions until the critical blockers above are resolved and verified.

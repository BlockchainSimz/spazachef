# SpazaChef v2 — isolated import and hardening work

This directory is an isolated staging area. It does not replace the existing repository application.

## Current contents
- `backend/app/main.py`: hardened API entrypoint patch.
- `backend/tests/test_security.py`: regression tests for fail-closed authentication and payment notifications.
- `PRODUCTION_READINESS_AUDIT.md`: engineering findings from the uploaded v2 snapshot.

## Important integration requirements
The full uploaded v2 source tree (frontend, recipe engine, SQLite store, package manifests, and remaining tests) still needs to be imported into this directory before it can be built or deployed as a standalone app. The existing `main` branch is a separate application and must not be overwritten.

## Security behavior in this staging patch
- Protected recipe endpoints reject missing or invalid Supabase JWTs.
- Missing JWT configuration returns 503 rather than silently granting anonymous access.
- PayFast ITN cannot grant paid tiers until provider source validation, server-side order matching, amount/currency checks, ownership, and idempotency are implemented.
- Recipe generation is performed before consuming the daily quota, so invalid recipe briefs do not consume quota.

## Validation
The uploaded snapshot's backend test suite passed locally after adding four security regression tests: 7 passed. Frontend dependency installation timed out in the available environment, so the production build remains unverified.

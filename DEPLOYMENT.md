# SpazaChef Deployment

SpazaChef uses a Vite frontend, a FastAPI backend and Supabase.

## Frontend on Vercel

Create/import a Vercel project with root directory `frontend`.

- Framework: Vite
- Install: `npm ci`
- Build: `npm run build`
- Output: `dist`

Set:

```text
VITE_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
VITE_SUPABASE_ANON_KEY=YOUR_PUBLIC_SUPABASE_PUBLISHABLE_KEY
VITE_API_URL=https://YOUR_API_DOMAIN
```

## Backend on Vercel

Create a second Vercel project using the same repository with root directory `backend`.

The serverless entry point is `api/index.py`. Dependencies are installed from `requirements.txt`.

Set these server-side environment variables in Vercel:

```text
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_ANON_KEY=YOUR_PUBLIC_SUPABASE_PUBLISHABLE_KEY
SUPABASE_SERVICE_ROLE_KEY=SET_IN_VERCEL
SUPABASE_JWT_SECRET=SET_IN_VERCEL
DATABASE_URL=SET_IN_VERCEL
REDIS_URL=SET_IN_VERCEL
JWT_SECRET=SET_IN_VERCEL
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
ANTHROPIC_API_KEY=SET_IN_VERCEL
ANTHROPIC_MODEL=claude-3-5-haiku-latest
ANTHROPIC_TIMEOUT_SECONDS=30
PAYFAST_MERCHANT_ID=SET_IN_VERCEL
PAYFAST_MERCHANT_KEY=SET_IN_VERCEL
PAYFAST_MODE=production
OZOW_API_KEY=SET_IN_VERCEL
OZOW_API_SECRET=SET_IN_VERCEL
ENV=production
DEBUG=false
ALLOWED_ORIGINS=https://YOUR_FRONTEND_DOMAIN
```

## Verification

Check the API after deployment:

```bash
curl https://YOUR_API_DOMAIN/health
```

Expected:

```json
{"status":"ok","service":"spazachef-api","version":"1.1.0"}
```

Then test:

1. frontend loads without console/build errors;
2. chef selection works;
3. recipe generation reaches `POST /api/v1/recipes/generate`;
4. follow-up reaches `POST /api/v1/recipes/followup`;
5. missing AI credentials produce a controlled 503 rather than a server crash.

## Security

Never commit production credentials. Any credential previously present in Git history must be rotated with its provider even after the file has been removed.

## Current deployment state

The repository is configured for deployment, but no SpazaChef Vercel project is currently connected to the available Vercel account. Deployment verification therefore requires the Vercel project to be imported/configured first.

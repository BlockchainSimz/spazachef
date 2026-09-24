# Vercel Deployment

SpazaChef is split into a Vite frontend and FastAPI backend.

## Frontend project

Import the repository into Vercel and set the project root to `frontend`.

- Framework preset: Vite
- Build command: `npm run build`
- Output directory: `dist`
- Install command: `npm ci`

Configure these Vercel environment variables:

```text
VITE_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
VITE_SUPABASE_ANON_KEY=YOUR_PUBLIC_SUPABASE_PUBLISHABLE_KEY
VITE_API_URL=https://YOUR_API_DOMAIN
```

## Backend project

Create a second Vercel project from the same repository and set its root directory to `backend`.

- Runtime: Python
- Install dependencies from `requirements.txt`
- The serverless entry point is `api/index.py`

Configure secrets in Vercel Project Settings; do not place them in Git:

```text
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_ANON_KEY=YOUR_PUBLIC_SUPABASE_PUBLISHABLE_KEY
SUPABASE_SERVICE_ROLE_KEY=SET_IN_VERCEL
SUPABASE_JWT_SECRET=SET_IN_VERCEL
DATABASE_URL=SET_IN_VERCEL
JWT_SECRET=SET_IN_VERCEL
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
ANTHROPIC_API_KEY=SET_IN_VERCEL
ANTHROPIC_MODEL=claude-3-5-haiku-latest
ANTHROPIC_TIMEOUT_SECONDS=30
ENV=production
DEBUG=false
ALLOWED_ORIGINS=https://YOUR_FRONTEND_DOMAIN
```

## Verification

After deployment:

```bash
curl https://YOUR_API_DOMAIN/health
```

Expected response:

```json
{"status":"ok","service":"spazachef-api","version":"1.1.0"}
```

Then open the frontend and exercise recipe generation and follow-up questions.

## Security

Any credential that was previously committed to this repository must be rotated in the originating provider. Removing a file from a branch does not erase credentials from Git history.

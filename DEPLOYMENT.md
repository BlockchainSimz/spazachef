# 🚀 SpazaChef Deployment Guide

This guide walks you through deploying SpazaChef to production on Vercel with Supabase.

## Quick Start (5 minutes)

1. **Supabase Setup**
   ```bash
   # Follow: docs/SUPABASE_SETUP.md
   # Get credentials from https://supabase.com/dashboard
   ```

2. **Vercel Deployment**
   ```bash
   # Frontend
   vercel --prod

   # Backend
   cd backend && vercel --prod
   ```

3. **Configure Secrets**
   - Add env vars to Vercel dashboard
   - Reference: `docs/VERCEL_DEPLOYMENT.md`

4. **Test**
   ```bash
   curl https://spazachef.vercel.app
   curl https://spazachef-api.vercel.app/health
   ```

## Full Deployment Checklist

**Complete Phase 1-10 in `docs/SETUP_CHECKLIST.md`**

## Documentation

- 📋 **Setup Checklist**: `docs/SETUP_CHECKLIST.md` (step-by-step)
- 🗄️ **Supabase Setup**: `docs/SUPABASE_SETUP.md` (database schemas + RLS)
- 🚀 **Vercel Guide**: `docs/VERCEL_DEPLOYMENT.md` (deployment details)
- 🏗️ **Architecture**: `docs/ARCHITECTURE.md` (system design)

## Key Links

- GitHub Repo: https://github.com/BlockchainSimz/spazachef
- Frontend: https://spazachef.vercel.app
- Backend API: https://spazachef-api.vercel.app
- Supabase: https://app.supabase.com (Project ID: bqffpvibvxusfxicssxz)
- Vercel: https://vercel.com/dashboard

## Environment Variables

### Frontend (.env.local)
```
VITE_SUPABASE_URL=https://bqffpvibvxusfxicssxz.supabase.co
VITE_SUPABASE_ANON_KEY=<anon_key>
VITE_API_URL=https://spazachef-api.vercel.app
```

### Backend (.env)
```
SUPABASE_URL=https://bqffpvibvxusfxicssxz.supabase.co
SUPABASE_KEY=<service_role_key>
JWT_SECRET=<secret>
PAYFAST_MERCHANT_ID=<id>
PAYFAST_MERCHANT_KEY=<key>
```

## Deployment Flow

```
GitHub (main branch)
    ↓
Vercel Auto-Deploy
    ↓
Frontend: spazachef.vercel.app ✅
Backend: spazachef-api.vercel.app ✅
    ↓
Connect to Supabase PostgreSQL ✅
    ↓
Production 🚀
```

## Support

- Issues: GitHub Issues
- Questions: Check docs/ folder
- Bugs: Create GitHub issue with:
  - Error message
  - Steps to reproduce
  - Expected vs actual behavior

---

**Ready to deploy?** Start with `docs/SETUP_CHECKLIST.md` ✨

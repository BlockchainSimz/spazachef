# 🚀 VERCEL DEPLOYMENT - READY TO GO

**Status**: ✅ Application pushed to GitHub - Ready for Vercel auto-deployment

---

## OPTION 1: Auto-Deploy from GitHub (Recommended)

Vercel automatically deploys when you push to GitHub. Since SpazaChef is already on GitHub, Vercel can pick it up immediately.

### Steps:

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard

2. **Import Frontend Project**:
   - Click "Add New" → "Project"
   - Click "Import Git Repository"
   - Search: `BlockchainSimz/spazachef`
   - Click "Import"
   - **Framework**: Vite
   - **Build Command**: `cd frontend && npm run build`
   - **Output Directory**: `frontend/dist`
   - **Install Command**: `cd frontend && npm install`
   - **Add Environment Variables** (Settings → Environment Variables):
     ```
     VITE_SUPABASE_URL = https://itkovoagalodjqfjvmlp.supabase.co
     VITE_SUPABASE_ANON_KEY = sb_publishable_aQGYuHXVJ7xah8ZXlw0Bhw_P8uBOBnf
     VITE_API_URL = https://spazachef-api.vercel.app
     ```
   - Click "Deploy"
   - **Result**: https://spazachef.vercel.app ✅

3. **Import Backend Project**:
   - Click "Add New" → "Project"
   - Click "Import Git Repository"
   - Search: `BlockchainSimz/spazachef` (again)
   - Click "Import"
   - **Project Name**: `spazachef-api`
   - **Framework**: Other
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Add Environment Variables** (Settings → Environment Variables):
     ```
     DATABASE_URL = postgresql://postgres:[$P@z@Ch3f@Pp]@db.itkovoagalodjqfjvmlp.supabase.co:5432/postgres
     SUPABASE_URL = https://itkovoagalodjqfjvmlp.supabase.co
     SUPABASE_ANON_KEY = sb_publishable_aQGYuHXVJ7xah8ZXlw0Bhw_P8uBOBnf
     SUPABASE_SERVICE_ROLE_KEY = [from Supabase Settings → API]
     SUPABASE_JWT_SECRET = [from Supabase Settings → Auth]
     JWT_SECRET = [generate: openssl rand -hex 32]
     JWT_ALGORITHM = HS256
     JWT_EXPIRATION_HOURS = 24
     DEBUG = false
     ENV = production
     ALLOWED_ORIGINS = https://spazachef.vercel.app
     ```
   - Click "Deploy"
   - **Result**: https://spazachef-api.vercel.app ✅

---

## OPTION 2: CLI Deployment

If you have Vercel CLI installed:

```bash
# Frontend
cd frontend
vercel --prod

# Backend
cd backend
vercel --prod --name spazachef-api
```

---

## OPTION 3: GitHub Integration (Automatic)

If you've already connected your GitHub to Vercel:

1. Push any commit to the `main` branch
2. Vercel automatically detects changes
3. Builds and deploys automatically
4. No manual steps needed

---

## After Deployment

### Test Frontend:
```bash
curl https://spazachef.vercel.app
# Should return: React app
```

### Test Backend:
```bash
curl https://spazachef-api.vercel.app/health
# Should return: {"status": "ok", "service": "spazachef-api"}
```

### Test Recipes API:
```bash
curl https://spazachef-api.vercel.app/api/v1/recipes
# Should return: JSON array with recipes
```

---

## Environment Variables Checklist

### Frontend (3 variables):
- [ ] VITE_SUPABASE_URL
- [ ] VITE_SUPABASE_ANON_KEY
- [ ] VITE_API_URL

### Backend (11 variables):
- [ ] DATABASE_URL
- [ ] SUPABASE_URL
- [ ] SUPABASE_ANON_KEY
- [ ] SUPABASE_SERVICE_ROLE_KEY
- [ ] SUPABASE_JWT_SECRET
- [ ] JWT_SECRET
- [ ] JWT_ALGORITHM
- [ ] JWT_EXPIRATION_HOURS
- [ ] DEBUG
- [ ] ENV
- [ ] ALLOWED_ORIGINS

---

## Status

✅ GitHub Repository: https://github.com/BlockchainSimz/spazachef
✅ Code Pushed: Ready for Vercel import
✅ Documentation: Complete
⏳ Deployment: Ready to deploy

**Next Step**: Go to https://vercel.com/dashboard and follow Option 1 above


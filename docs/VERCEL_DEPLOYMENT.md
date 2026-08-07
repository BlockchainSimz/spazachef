# Vercel Deployment Guide for SpazaChef

## Overview

SpazaChef is deployed on Vercel with:
- **Frontend**: spazachef.vercel.app (Next.js/React)
- **Backend API**: spazachef-api.vercel.app (FastAPI serverless)

## Prerequisites

- Vercel account (https://vercel.com)
- Supabase project configured
- GitHub repository connected
- Environment secrets configured

## Step 1: Connect GitHub Repository

1. Go to https://vercel.com/dashboard
2. Click **"Add New..."** → **"Project"**
3. Select **"Import Git Repository"**
4. Search for `BlockchainSimz/spazachef`
5. Click **"Import"**

## Step 2: Configure Frontend Deployment

### 2.1 Project Settings
- **Framework**: Vite
- **Build Command**: `cd frontend && npm run build`
- **Output Directory**: `frontend/dist`
- **Install Command**: `cd frontend && npm install`

### 2.2 Environment Variables (Frontend)
Add these in **Settings** → **Environment Variables**:

```
VITE_SUPABASE_URL=https://bqffpvibvxusfxicssxz.supabase.co
VITE_SUPABASE_ANON_KEY=<your_supabase_anon_key>
VITE_API_URL=https://spazachef-api.vercel.app
```

### 2.3 Deploy Frontend
```bash
# Option 1: Via Vercel Dashboard (automatic on push)
# Push to main branch and Vercel deploys automatically

# Option 2: Via Vercel CLI
npm install -g vercel
cd frontend
vercel --prod
```

**Frontend URL**: https://spazachef.vercel.app

## Step 3: Configure Backend Deployment

### 3.1 Create API Project
1. Go to Vercel Dashboard
2. Click **"Add New..."** → **"Project"**
3. Import `BlockchainSimz/spazachef` again
4. Name it: `spazachef-api`

### 3.2 Project Settings
- **Framework**: Other (FastAPI)
- **Build Command**: `pip install -r backend/requirements.txt`
- **Output Directory**: `backend`
- **Install Command**: (Leave empty)

### 3.3 Environment Variables (Backend)
Add in **Settings** → **Environment Variables**:

```
SUPABASE_URL=https://bqffpvibvxusfxicssxz.supabase.co
SUPABASE_KEY=<your_supabase_service_role_key>
SUPABASE_JWT_SECRET=<your_jwt_secret>
JWT_SECRET=<your_jwt_secret>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

PAYFAST_MERCHANT_ID=<your_payfast_id>
PAYFAST_MERCHANT_KEY=<your_payfast_key>
PAYFAST_MODE=test

OZOW_API_KEY=<your_ozow_key>
OZOW_API_SECRET=<your_ozow_secret>

REDIS_URL=<your_redis_url>
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

DEBUG=false
ENV=production
```

### 3.4 Deploy Backend
```bash
# Via CLI
vercel --prod --cwd backend
```

**Backend API URL**: https://spazachef-api.vercel.app

## Step 4: GitHub Secrets Configuration

Add these secrets to GitHub (Settings → Secrets and variables → Actions):

```
VERCEL_ORG_ID=<your_vercel_org_id>
VERCEL_PROJECT_ID=<frontend_project_id>
VERCEL_API_PROJECT_ID=<backend_project_id>
VERCEL_TOKEN=<your_vercel_api_token>

SUPABASE_URL=https://bqffpvibvxusfxicssxz.supabase.co
SUPABASE_KEY=<your_supabase_service_role_key>
JWT_SECRET=<your_jwt_secret>
PAYFAST_MERCHANT_ID=<your_payfast_id>
PAYFAST_MERCHANT_KEY=<your_payfast_key>
```

**To get Vercel Token**:
1. Go to https://vercel.com/account/tokens
2. Click "Create"
3. Name: `spazachef-ci`
4. Copy and add to GitHub secrets

## Step 5: Configure Domains

### 5.1 Frontend Domain
1. Go to **Project Settings** → **Domains**
2. Add custom domain or use default: `spazachef.vercel.app`
3. Configure DNS (if custom domain)

### 5.2 Backend API Domain
1. Configure: `spazachef-api.vercel.app`
2. Or custom: `api.spazachef.com`

## Step 6: Set Up Continuous Deployment

### 6.1 Enable Auto-Deploy
- **Branch**: `main`
- **Auto-deploy**: ✅ Enabled
- **Preview deployments**: ✅ Enabled

### 6.2 GitHub Actions Workflow
The `.github/workflows/deploy-vercel.yml` automatically:
1. Runs on push to `main`
2. Builds both frontend and backend
3. Deploys to Vercel
4. Creates preview deployments for PRs

**Trigger deployment**:
```bash
git push origin main
```

## Step 7: Test Deployments

### Test Frontend
```bash
curl https://spazachef.vercel.app/health
# Expected: Connection to API health check
```

### Test API
```bash
curl https://spazachef-api.vercel.app/health
# Expected: {"status": "ok", "service": "spazachef-api"}
```

### Test Database Connection
```bash
curl https://spazachef-api.vercel.app/api/v1
# Expected: API endpoints list
```

## Step 8: Monitoring & Logs

### View Logs
1. **Vercel Dashboard** → **Project** → **Deployments**
2. Click deployment → **Logs**
3. View build and runtime logs

### Monitor Performance
- **Analytics**: Dashboard → Analytics
- **Metrics**: Speed, requests, errors
- **Flamegraph**: Performance analysis

### Error Tracking
- **Errors**: Dashboard → Monitoring
- **Alerts**: Set up alerts for failures

## Step 9: Rollback Strategy

### Rollback Previous Deployment
1. Go to **Deployments** tab
2. Find previous stable deployment
3. Click **⋮** → **Promote to Production**

### Manual Rollback
```bash
# Revert to previous commit
git revert <commit_hash>
git push origin main  # Auto-redeploys
```

## Step 10: Custom Domains (Optional)

### Add Custom Domain
1. **Project Settings** → **Domains**
2. Add domain: `spazachef.dev`
3. Update DNS records:
   ```
   Type: CNAME
   Name: spazachef
   Value: cname.vercel.app
   ```

### SSL/TLS
- Automatic via Vercel
- Free Let's Encrypt certificates
- Auto-renewal

## Troubleshooting

### Build Fails
```bash
# Check build logs in Vercel dashboard
# Common issues:
# 1. Missing env vars - add to Settings
# 2. Node version - set in vercel.json
# 3. Dependencies - ensure requirements.txt is complete
```

### API 502 Errors
```bash
# 1. Check backend logs in Vercel dashboard
# 2. Verify Supabase connection string
# 3. Check Redis connection
# 4. Review error logs at https://spazachef-api.vercel.app/logs
```

### CORS Errors
```bash
# Frontend logs: Check browser console
# 1. Verify ALLOWED_ORIGINS in backend config
# 2. Check CORS middleware in app/main.py
# 3. Restart backend deployment
```

## Cost Optimization

- **Vercel Pricing**: Free tier covers most startups
- **Supabase**: ~$25/month for reasonable usage
- **Redis**: ~$5-15/month (Upstash)
- **Total**: ~$30-40/month initially

## Security Best Practices

1. **Never commit .env files**
2. **Use GitHub Secrets** for sensitive data
3. **Enable 2FA** on Vercel account
4. **Rotate API keys** quarterly
5. **Monitor build logs** for leaks
6. **Use preview deployments** for testing PRs

## Next Steps

1. ✅ Deploy frontend
2. ✅ Deploy backend
3. ✅ Test end-to-end
4. ✅ Set up monitoring
5. ✅ Configure production database
6. ✅ Set up backups
7. ✅ Monitor costs

---

**Deployment Status**: Ready for production
**Last Updated**: 2026-08-07

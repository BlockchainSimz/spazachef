# SpazaChef Setup Checklist

Complete this checklist to deploy SpazaChef to production with Vercel and Supabase.

## Phase 1: Supabase Setup ✅

### Create Supabase Project
- [ ] Go to https://supabase.com/dashboard
- [ ] Click "New Project"
- [ ] Name: `spazachef`
- [ ] Database Password: Generate strong password
- [ ] Region: Select closest to South Africa (EU or US-East)
- [ ] Note your **Project URL** and **API Keys**

### Database Setup
- [ ] Run SQL schemas from `docs/SUPABASE_SETUP.md`
  - [ ] Create `users` table
  - [ ] Create `recipes` table
  - [ ] Create `recipe_favorites` table
  - [ ] Create `subscriptions` table
  - [ ] Create `payment_webhooks` table
  - [ ] Enable pgvector extension
  - [ ] Set up Row Level Security (RLS)
  - [ ] Create search function

### Authentication Setup
- [ ] Enable Email provider
- [ ] Configure SMTP (if using transactional emails)
- [ ] Set JWT expiration (24 hours recommended)
- [ ] Copy JWT Secret

### Get Credentials
- [ ] Copy Project URL: `https://bqffpvibvxusfxicssxz.supabase.co`
- [ ] Copy Anon Public Key (for frontend)
- [ ] Copy Service Role Key (for backend - keep secret!)
- [ ] Copy JWT Secret

**Save these in a secure location** (KeePass, 1Password, etc.)

---

## Phase 2: Vercel Setup

### Vercel Account
- [ ] Create account at https://vercel.com
- [ ] Verify email
- [ ] Create new team (optional): `spazachef`

### Generate Vercel Token
- [ ] Go to https://vercel.com/account/tokens
- [ ] Click "Create"
- [ ] Name: `spazachef-ci`
- [ ] Scope: Full Account
- [ ] Copy token to safe location

### Connect GitHub Repository
- [ ] Go to https://vercel.com/new
- [ ] Click "Import Git Repository"
- [ ] Search: `BlockchainSimz/spazachef`
- [ ] Click "Import"

---

## Phase 3: Frontend Deployment

### Create Frontend Project
- [ ] In Vercel Dashboard, click "Add New" → "Project"
- [ ] Import `BlockchainSimz/spazachef`
- [ ] Name: `spazachef` (or `spazachef-web`)

### Configure Frontend Project
- [ ] **Framework**: Vite
- [ ] **Build Command**: `cd frontend && npm run build`
- [ ] **Output Directory**: `frontend/dist`
- [ ] **Install Command**: `cd frontend && npm install`

### Add Environment Variables (Frontend)
Go to **Project Settings** → **Environment Variables**:

```
VITE_SUPABASE_URL = https://bqffpvibvxusfxicssxz.supabase.co
VITE_SUPABASE_ANON_KEY = <paste_anon_public_key_here>
VITE_API_URL = https://spazachef-api.vercel.app
```

- [ ] Add to `Production` environment
- [ ] Add to `Preview` environment
- [ ] Save and redeploy

### Deploy
- [ ] Click "Deploy"
- [ ] Wait for build to complete
- [ ] Test: Visit https://spazachef.vercel.app/health

**Frontend URL**: `https://spazachef.vercel.app`

---

## Phase 4: Backend Deployment

### Create Backend Project
- [ ] In Vercel Dashboard, click "Add New" → "Project"
- [ ] Import `BlockchainSimz/spazachef`
- [ ] Name: `spazachef-api`

### Configure Backend Project
- [ ] **Framework**: Other
- [ ] **Build Command**: `pip install -r backend/requirements.txt`
- [ ] **Root Directory**: `backend`

### Add Environment Variables (Backend)
Go to **Project Settings** → **Environment Variables**:

**Database**:
```
SUPABASE_URL = https://bqffpvibvxusfxicssxz.supabase.co
SUPABASE_KEY = <paste_service_role_key_here>
SUPABASE_JWT_SECRET = <paste_jwt_secret_here>
```

**JWT**:
```
JWT_SECRET = <your_secure_secret_min_32_chars>
JWT_ALGORITHM = HS256
JWT_EXPIRATION_HOURS = 24
```

**Payment Processing**:
```
PAYFAST_MERCHANT_ID = <your_payfast_merchant_id>
PAYFAST_MERCHANT_KEY = <your_payfast_merchant_key>
PAYFAST_MODE = test

OZOW_API_KEY = <your_ozow_api_key>
OZOW_API_SECRET = <your_ozow_secret>
```

**Other**:
```
REDIS_URL = <your_redis_url>
DEBUG = false
ENV = production
ALLOWED_ORIGINS = https://spazachef.vercel.app,https://www.spazachef.dev
```

- [ ] Add to `Production` environment
- [ ] Save and redeploy

### Deploy
- [ ] Click "Deploy"
- [ ] Wait for build to complete
- [ ] Test: `curl https://spazachef-api.vercel.app/health`

**Backend URL**: `https://spazachef-api.vercel.app`

---

## Phase 5: GitHub Secrets (Optional CI/CD)

Add to GitHub repository **Settings** → **Secrets and variables** → **Actions**:

### Vercel Secrets
```
VERCEL_ORG_ID = <your_vercel_org_id>
VERCEL_PROJECT_ID = <frontend_project_id>
VERCEL_API_PROJECT_ID = <backend_project_id>
VERCEL_TOKEN = <your_vercel_api_token>
```

### Supabase Secrets
```
SUPABASE_URL = https://bqffpvibvxusfxicssxz.supabase.co
SUPABASE_KEY = <service_role_key>
JWT_SECRET = <your_jwt_secret>
```

### Payment Secrets
```
PAYFAST_MERCHANT_ID = <merchant_id>
PAYFAST_MERCHANT_KEY = <merchant_key>
```

- [ ] All secrets added
- [ ] No secrets committed to repo
- [ ] `.env` files in `.gitignore`

---

## Phase 6: Testing

### Frontend Tests
- [ ] Visit https://spazachef.vercel.app
- [ ] Page loads without errors
- [ ] Browser console has no errors
- [ ] Can reach API: Check Network tab

### Backend Tests
```bash
# Health check
curl https://spazachef-api.vercel.app/health

# API status
curl https://spazachef-api.vercel.app/api/v1

# Expected responses:
# {"status": "ok", "service": "spazachef-api"}
```

### Database Tests
- [ ] Connect to Supabase via psql or web console
- [ ] Run: `SELECT * FROM recipes;` (should be empty or seeded)
- [ ] Check vector extension: `SELECT extname FROM pg_extension;`

### End-to-End Flow
- [ ] User can sign up (if auth enabled)
- [ ] User can view recipes
- [ ] User can search recipes
- [ ] User can favorite recipes (if logged in)

---

## Phase 7: Production Configuration

### Domain Setup
- [ ] Register domain (optional): `spazachef.dev` or `spazachef.co.za`
- [ ] In Vercel: **Project Settings** → **Domains**
- [ ] Add custom domain
- [ ] Update DNS records (CNAME to `cname.vercel.app`)
- [ ] Wait for DNS propagation (5-48 hours)

### SSL/TLS
- [ ] Vercel auto-issues Let's Encrypt certificate
- [ ] Verify HTTPS works
- [ ] Set HSTS header (optional)

### Payment Gateway Setup
- [ ] Set up PayFast account: https://www.payfast.co.za
- [ ] Get Merchant ID and Key
- [ ] Add to Vercel environment variables
- [ ] Test payment flow in sandbox mode
- [ ] Configure webhook URL: `https://spazachef-api.vercel.app/api/webhooks/payfast`

### Analytics Setup
- [ ] Enable Vercel Analytics: **Settings** → **Analytics**
- [ ] Set up error tracking
- [ ] Configure alerts for high error rates

---

## Phase 8: Monitoring & Maintenance

### Daily Checks
- [ ] Visit dashboard: https://vercel.com/dashboard
- [ ] Check error rates
- [ ] Review recent deployments
- [ ] Check Supabase metrics

### Weekly Tasks
- [ ] Review logs for errors
- [ ] Monitor API response times
- [ ] Check database size
- [ ] Review error logs

### Monthly Tasks
- [ ] Update dependencies: `npm update`, `pip install -U`
- [ ] Rotate API keys (if using long-lived tokens)
- [ ] Review security settings
- [ ] Backup Supabase database

### Quarterly Tasks
- [ ] Performance audit
- [ ] Security audit
- [ ] Cost review
- [ ] Feature planning

---

## Phase 9: Backup & Recovery

### Database Backups
- [ ] Go to Supabase: **Settings** → **Backups**
- [ ] Enable daily backups (automatic)
- [ ] Download backup weekly
- [ ] Store in secure location (Google Drive, S3, etc.)

### Code Backups
- [ ] GitHub repo is your code backup
- [ ] Keep main branch clean (only production-ready)
- [ ] Tag releases: `git tag -a v1.0.0 -m "Production release"`

### Recovery Plan
- [ ] Document recovery procedures
- [ ] Test recovery process quarterly
- [ ] Keep list of all API keys/secrets
- [ ] Store recovery docs offline

---

## Phase 10: Post-Launch

### Marketing
- [ ] Update website with links
- [ ] Submit to directories (if applicable)
- [ ] Announce on social media
- [ ] Gather feedback from users

### Optimization
- [ ] Monitor Core Web Vitals
- [ ] Optimize images and assets
- [ ] Cache optimization
- [ ] Database query optimization

### Scaling
- [ ] Monitor traffic growth
- [ ] Set up CDN (Vercel handles this)
- [ ] Consider database read replicas if needed
- [ ] Plan for storage scaling

---

## Checklist Summary

Total items: 100+
- [ ] Phase 1: Supabase (10+ items)
- [ ] Phase 2: Vercel Setup (5+ items)
- [ ] Phase 3: Frontend (10+ items)
- [ ] Phase 4: Backend (15+ items)
- [ ] Phase 5: GitHub (10+ items)
- [ ] Phase 6: Testing (10+ items)
- [ ] Phase 7: Production (10+ items)
- [ ] Phase 8: Monitoring (10+ items)
- [ ] Phase 9: Backups (5+ items)
- [ ] Phase 10: Launch (10+ items)

---

## Quick Reference

| Component | Status | URL |
|-----------|--------|-----|
| Repository | ✅ Created | https://github.com/BlockchainSimz/spazachef |
| Frontend | ⏳ To Deploy | https://spazachef.vercel.app |
| Backend API | ⏳ To Deploy | https://spazachef-api.vercel.app |
| Database | ⏳ To Setup | Supabase (bqffpvibvxusfxicssxz) |
| Documentation | ✅ Complete | docs/ folder |

---

**Last Updated**: 2026-08-07
**Status**: Ready for deployment

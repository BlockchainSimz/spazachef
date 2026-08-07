# 🔐 SpazaChef Credentials Guide

This guide explains all the credentials you need and where to find them.

## Your Supabase Project

- **Project ID**: `itkovoagalodjqfjvmlp`
- **Project URL**: `https://itkovoagalodjqfjvmlp.supabase.co`
- **Console**: https://app.supabase.com

---

## Supabase API Keys

### Publishable Key (Anon Key) ✅
```
sb_publishable_aQGYuHXVJ7xah8ZXlw0Bhw_P8uBOBnf
```

**Where to use**:
- ✅ Frontend (.env.local / Vercel env vars)
- ✅ Public API calls
- ❌ Never use for sensitive backend operations

**In your code**:
```javascript
// Frontend
VITE_SUPABASE_ANON_KEY=sb_publishable_aQGYuHXVJ7xah8ZXlw0Bhw_P8uBOBnf
```

---

### Service Role Key (Secret!) 🔐
**Location**: Supabase Dashboard → Settings → API → Service Role Secret

**Where to use**:
- ✅ Backend only (FastAPI, Node, etc.)
- ❌ Never commit to GitHub
- ❌ Never share publicly

**In your code**:
```bash
# Backend .env (private, never commit)
SUPABASE_SERVICE_ROLE_KEY=eyJ... (get from Supabase)
```

**How to find it**:
1. Go to https://app.supabase.com
2. Select project: `itkovoagalodjqfjvmlp`
3. Click **Settings** (left sidebar)
4. Click **API**
5. Under "Project API keys" → Copy "Service Role"
6. Paste into `backend/.env` (keep secret!)

---

### JWT Secret 🔑
**Location**: Supabase Dashboard → Settings → Auth → JWT Secret

**Where to use**:
- ✅ Backend for token validation
- ❌ Never expose to frontend
- ❌ Keep it secret!

**How to find it**:
1. Go to https://app.supabase.com
2. Select project: `itkovoagalodjqfjvmlp`
3. Click **Settings** (left sidebar)
4. Click **Auth**
5. Copy JWT Secret
6. Paste into `backend/.env` as `SUPABASE_JWT_SECRET`

---

## Environment Variable Setup

### Frontend (.env.local)
```bash
# Supabase - PUBLIC (OK to expose to frontend)
VITE_SUPABASE_URL=https://itkovoagalodjqfjvmlp.supabase.co
VITE_SUPABASE_ANON_KEY=sb_publishable_aQGYuHXVJ7xah8ZXlw0Bhw_P8uBOBnf

# API - Depends on deployment
VITE_API_URL=https://spazachef-api.vercel.app  # Production
VITE_API_DEV_URL=http://localhost:8000         # Local dev
```

**Never include**:
- ❌ Service role key
- ❌ JWT secret
- ❌ Private API keys

---

### Backend (.env)
```bash
# Supabase - PRIVATE (keep secret!)
SUPABASE_URL=https://itkovoagalodjqfjvmlp.supabase.co
SUPABASE_ANON_KEY=sb_publishable_aQGYuHXVJ7xah8ZXlw0Bhw_P8uBOBnf
SUPABASE_SERVICE_ROLE_KEY=[get from Supabase Settings → API]
SUPABASE_JWT_SECRET=[get from Supabase Settings → Auth]

# JWT Configuration
JWT_SECRET=your_super_secret_key_min_32_chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Payment (Optional, set when ready)
PAYFAST_MERCHANT_ID=
PAYFAST_MERCHANT_KEY=
PAYFAST_MODE=test

# Redis (Local dev only)
REDIS_URL=redis://localhost:6379

# Application
DEBUG=false           # true for dev, false for prod
ENV=production        # production or development
ALLOWED_ORIGINS=https://spazachef.vercel.app
```

**File handling**:
- ✅ Store in `.env` (local machine only)
- ✅ Add to Vercel Settings → Environment Variables
- ❌ Never commit `.env` to GitHub
- ✅ `.env.example` shows template (committed to GitHub)

---

## Vercel Deployment Setup

### Environment Variables in Vercel Dashboard

**Frontend Project** (`spazachef`):
1. Go to **Project Settings** → **Environment Variables**
2. Add:
   ```
   VITE_SUPABASE_URL = https://itkovoagalodjqfjvmlp.supabase.co
   VITE_SUPABASE_ANON_KEY = sb_publishable_aQGYuHXVJ7xah8ZXlw0Bhw_P8uBOBnf
   VITE_API_URL = https://spazachef-api.vercel.app
   ```

**Backend Project** (`spazachef-api`):
1. Go to **Project Settings** → **Environment Variables**
2. Add:
   ```
   SUPABASE_URL = https://itkovoagalodjqfjvmlp.supabase.co
   SUPABASE_ANON_KEY = sb_publishable_aQGYuHXVJ7xah8ZXlw0Bhw_P8uBOBnf
   SUPABASE_SERVICE_ROLE_KEY = [from Supabase Settings]
   SUPABASE_JWT_SECRET = [from Supabase Settings]
   JWT_SECRET = [generate: openssl rand -hex 32]
   JWT_ALGORITHM = HS256
   JWT_EXPIRATION_HOURS = 24
   DEBUG = false
   ENV = production
   ALLOWED_ORIGINS = https://spazachef.vercel.app
   ```

---

## Generating Secure Secrets

### Generate JWT Secret (if you need your own)
```bash
# macOS/Linux
openssl rand -hex 32

# Windows (PowerShell)
[Convert]::ToHexString((New-Object System.Security.Cryptography.RNGCryptoServiceProvider).GetBytes(32))

# Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

Copy the output and use as `JWT_SECRET` in backend `.env`

---

## Security Best Practices

✅ **DO**:
- Store secrets in `.env` files (local only)
- Use `.env.example` to track what variables you need
- Add `.env` to `.gitignore` (already done)
- Rotate secrets every 90 days
- Use service role key only on backend
- Use anon key only on frontend

❌ **DON'T**:
- Commit `.env` files to GitHub
- Share secrets in Slack/Email
- Use same secret for dev & prod
- Commit credentials to code
- Use weak passwords for JWT secret
- Share service role key with anyone

---

## Verifying Your Setup

### Test Frontend Connection
```bash
cd frontend
npm install
npm run dev  # Should connect to Supabase without errors
```

### Test Backend Connection
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# In another terminal:
curl http://localhost:8000/health
# Should return: {"status": "ok", "service": "spazachef-api"}
```

### Test Database Connection
```bash
# In backend terminal:
curl http://localhost:8000/api/v1/recipes
# Should return: List of recipes from Supabase
```

---

## Troubleshooting

### "Invalid API Key"
- Verify you're using the correct key (anon vs service role)
- Check the URL is correct: `https://itkovoagalodjqfjvmlp.supabase.co`
- Regenerate keys if needed (Supabase Dashboard → Settings → API)

### "CORS Error"
- Add your frontend URL to `ALLOWED_ORIGINS` in backend
- For Vercel: `https://spazachef.vercel.app`
- For local: `http://localhost:5173`

### "Permission Denied"
- Backend must use `service_role key` (not anon key)
- Frontend must use `anon key` (not service role)
- Check RLS policies in Supabase

### "Connection Refused"
- Verify Supabase project is running
- Check internet connection
- Verify URL is correct: `https://itkovoagalodjqfjvmlp.supabase.co`

---

## Credentials Checklist

✅ **Required for Frontend**:
- [ ] `VITE_SUPABASE_URL`
- [ ] `VITE_SUPABASE_ANON_KEY` (this one: `sb_publishable_aQGYuHXVJ7xah8ZXlw0Bhw_P8uBOBnf`)
- [ ] `VITE_API_URL`

✅ **Required for Backend**:
- [ ] `SUPABASE_URL`
- [ ] `SUPABASE_ANON_KEY`
- [ ] `SUPABASE_SERVICE_ROLE_KEY` (from Supabase Settings)
- [ ] `SUPABASE_JWT_SECRET` (from Supabase Settings)
- [ ] `JWT_SECRET` (generate new or use existing)

✅ **For Vercel Deployment**:
- [ ] All frontend vars in frontend project
- [ ] All backend vars in backend project
- [ ] Applied to Production environment

---

**Status**: ✅ Your anon key is configured. Get service role key & JWT secret from Supabase to complete setup.

**Next Steps**:
1. Go to Supabase: https://app.supabase.com
2. Select project: `itkovoagalodjqfjvmlp`
3. Get Service Role Key (Settings → API)
4. Get JWT Secret (Settings → Auth)
5. Add to Vercel environment variables
6. Deploy! 🚀


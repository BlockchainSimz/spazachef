# 🔌 SpazaChef Database Connection Guide

## Your Direct Connection String

```
postgresql://postgres:[$P@z@Ch3f@Pp]@db.itkovoagalodjqfjvmlp.supabase.co:5432/postgres
```

**⚠️ IMPORTANT**: This contains your database password. Keep it **SECRET**!

---

## Connection Details

| Setting | Value |
|---------|-------|
| **Host** | `db.itkovoagalodjqfjvmlp.supabase.co` |
| **Port** | `5432` |
| **Database** | `postgres` |
| **User** | `postgres` |
| **Password** | `[$P@z@Ch3f@Pp]` |

---

## Where to Use

### ✅ Backend (.env)
```bash
DATABASE_URL=postgresql://postgres:[$P@z@Ch3f@Pp]@db.itkovoagalodjqfjvmlp.supabase.co:5432/postgres
```

### ✅ Local Development
```bash
# .env file (never commit)
DATABASE_URL=postgresql://postgres:[$P@z@Ch3f@Pp]@db.itkovoagalodjqfjvmlp.supabase.co:5432/postgres
```

### ✅ Vercel Backend Deployment
Add to **Project Settings** → **Environment Variables**:
```
DATABASE_URL = postgresql://postgres:[$P@z@Ch3f@Pp]@db.itkovoagalodjqfjvmlp.supabase.co:5432/postgres
```

### ❌ Frontend
**NEVER** add this to frontend - it contains your password!

### ❌ GitHub
**NEVER** commit this to GitHub - add to `.gitignore`

---

## Testing Connection

### From Command Line (psql)
```bash
psql postgresql://postgres:[$P@z@Ch3f@Pp]@db.itkovoagalodjqfjvmlp.supabase.co:5432/postgres

# Should show:
# psql (14.0, server 14.x)
# Type "help" for help.
# postgres=>
```

### From Python (Backend)
```python
from sqlalchemy import create_engine

DATABASE_URL = "postgresql://postgres:[$P@z@Ch3f@Pp]@db.itkovoagalodjqfjvmlp.supabase.co:5432/postgres"
engine = create_engine(DATABASE_URL)

# Test connection
with engine.connect() as conn:
    result = conn.execute("SELECT 1")
    print(result.fetchone())  # (1,)
```

### From FastAPI
```python
from app.config import settings

# In your FastAPI app, when you deploy:
# 1. Add DATABASE_URL to Vercel env vars
# 2. Backend will automatically use it
# 3. All database queries will work
```

---

## SQLAlchemy Configuration

The backend is already configured to use this connection string. In `backend/app/config.py`:

```python
class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://..."  # Will use env var when deployed
```

When you set `DATABASE_URL` in Vercel environment variables, SQLAlchemy will automatically connect to your Supabase database.

---

## Alembic Migrations (Database Updates)

To run migrations against your Supabase database:

```bash
# Local development
export DATABASE_URL=postgresql://postgres:[$P@z@Ch3f@Pp]@db.itkovoagalodjqfjvmlp.supabase.co:5432/postgres
alembic upgrade head

# Or with the connection string directly
cd backend
alembic upgrade head
```

---

## Security Best Practices

✅ **DO**:
- Store connection string in `.env` (local only)
- Add to Vercel environment variables (secure)
- Rotate password every 90 days
- Use strong passwords (yours is strong ✓)
- Restrict IP access (if Supabase supports it)

❌ **DON'T**:
- Commit `.env` to GitHub
- Share connection string via Slack/Email
- Use in frontend code
- Log connection string in error messages
- Store in version control

---

## Verifying Database Access

### Step 1: Check Tables Exist
In Vercel backend logs or local terminal:
```bash
curl http://localhost:8000/api/v1/recipes
# Should return recipes from database
```

### Step 2: Check Data
In Supabase Console → SQL Editor:
```sql
SELECT COUNT(*) FROM recipes;
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM subscriptions;
```

### Step 3: Test Queries
```bash
# From your backend application:
GET /api/v1/recipes          # List recipes
POST /api/v1/recipes/search  # Search recipes
```

---

## Troubleshooting

### "Connection refused"
- Check internet connection
- Verify host: `db.itkovoagalodjqfjvmlp.supabase.co`
- Verify port: `5432`
- Check Supabase project is running

### "Authentication failed"
- Check password: `[$P@z@Ch3f@Pp]`
- Verify username: `postgres`
- Try resetting password in Supabase Dashboard

### "Database does not exist"
- Database is `postgres` (not a separate db)
- All tables should be in `public` schema

### "SSL Error"
- Supabase requires SSL connections
- Connection string already includes SSL
- If issues persist, add: `?sslmode=require`

### Firewall Issues
- Supabase allows connections from anywhere by default
- If blocked, check Supabase security settings
- Add your IP to allowlist if needed

---

## Connection String Format

Breaking down the full connection string:

```
postgresql://
  postgres              ← username
  :[$P@z@Ch3f@Pp]     ← password
  @db.itkovoagalodjqfjvmlp.supabase.co  ← host
  :5432                ← port
  /postgres            ← database name
```

All components are required. If any part is wrong, connection fails.

---

## For Different Frameworks

### FastAPI (Already Configured ✅)
```python
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
```

### Django
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': '[$P@z@Ch3f@Pp]',
        'HOST': 'db.itkovoagalodjqfjvmlp.supabase.co',
        'PORT': '5432',
    }
}
```

### Node.js
```javascript
const connectionString = process.env.DATABASE_URL;
const pool = new Pool({ connectionString });
```

### Python (asyncpg)
```python
import asyncpg
conn = await asyncpg.connect(DATABASE_URL)
```

---

## Backup & Disaster Recovery

### Supabase Automatic Backups
- ✅ Daily automated backups (7 days retention)
- ✅ Access via Supabase Dashboard → Settings → Backups
- ✅ Download backups for safe storage

### Manual Backup
```bash
# Dump your entire database
pg_dump postgresql://postgres:[$P@z@Ch3f@Pp]@db.itkovoagalodjqfjvmlp.supabase.co:5432/postgres > backup.sql

# Restore from backup
psql postgresql://postgres:[$P@z@Ch3f@Pp]@db.itkovoagalodjqfjvmlp.supabase.co:5432/postgres < backup.sql
```

### Cloud Storage Backup
Store backups in Google Drive, AWS S3, or Dropbox for redundancy.

---

## Next Steps

1. ✅ You have connection string
2. ✅ Add to Vercel environment variables
3. ⏳ Deploy backend to Vercel
4. ⏳ Test database connection
5. ⏳ Run SQL setup from SUPABASE_PROJECT_SETUP.md
6. ⏳ Verify data in Supabase Console

---

**Status**: ✅ Ready for deployment
**Connection String**: Active
**Security**: Secret password configured


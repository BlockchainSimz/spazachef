# SpazaChef Supabase Setup - Project itkovoagalodjqfjvmlp

**Supabase Project URL**: https://itkovoagalodjqfjvmlp.supabase.co

## Step 1: Access Your Supabase Project

1. Go to https://app.supabase.com
2. Select your project: **itkovoagalodjqfjvmlp**
3. Navigate to **SQL Editor** (left sidebar)

## Step 2: Run Database Setup

1. Click **"New Query"**
2. Copy and paste the entire SQL script below:

```sql
-- SpazaChef Database Setup
-- Enable extensions
CREATE EXTENSION IF NOT EXISTS vector;

-- Users Table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  full_name TEXT,
  subscription_tier TEXT DEFAULT 'free',
  subscription_status TEXT DEFAULT 'inactive',
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_users_email ON users(email);

-- Recipes Table
CREATE TABLE recipes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  description TEXT,
  category TEXT NOT NULL,
  chef_name TEXT,
  ingredients JSONB,
  instructions JSONB,
  prep_time_minutes INT,
  cook_time_minutes INT,
  servings INT DEFAULT 4,
  difficulty TEXT DEFAULT 'medium',
  embedding vector(384),
  image_url TEXT,
  likes_count INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_recipes_category ON recipes(category);
CREATE INDEX idx_recipes_chef ON recipes(chef_name);
CREATE INDEX idx_recipes_embedding ON recipes USING ivfflat (embedding vector_cosine_ops);

-- Recipe Favorites
CREATE TABLE recipe_favorites (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  recipe_id UUID NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
  created_at TIMESTAMP DEFAULT now(),
  UNIQUE(user_id, recipe_id)
);

-- Subscriptions
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  tier TEXT NOT NULL,
  status TEXT DEFAULT 'active',
  payfast_reference TEXT UNIQUE,
  renewal_date DATE,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- Payment Webhooks
CREATE TABLE payment_webhooks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider TEXT NOT NULL,
  reference TEXT,
  payload JSONB,
  status TEXT,
  user_id UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT now()
);

-- Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE recipes ENABLE ROW LEVEL SECURITY;
ALTER TABLE recipe_favorites ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own profile" ON users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON users FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Anyone can view recipes" ON recipes FOR SELECT USING (true);
CREATE POLICY "Users can view own favorites" ON recipe_favorites FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create own favorites" ON recipe_favorites FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete own favorites" ON recipe_favorites FOR DELETE USING (auth.uid() = user_id);
CREATE POLICY "Users can view own subscription" ON subscriptions FOR SELECT USING (auth.uid() = user_id);

-- Sample Recipes
INSERT INTO recipes (title, description, category, chef_name, ingredients, instructions, prep_time_minutes, cook_time_minutes, difficulty) VALUES
('Umqombothi', 'Traditional Zulu fermented beer', 'Beverages', 'Gogo Precious', 
 '{"items": ["Maize meal", "Sorghum", "Ginger"]}',
 '{"steps": ["Boil grain", "Cool", "Ferment 3 days"]}', 30, 180, 'medium'),
('Umngqusho', 'Cracked corn and beans', 'Main Courses', 'Chef Mandla',
 '{"items": ["Maize corn", "Beans", "Onion"]}',
 '{"steps": ["Cook beans", "Add corn", "Simmer"]}', 15, 60, 'easy'),
('Sosaties', 'Spiced meat skewers', 'Braai', 'Boet Frik',
 '{"items": ["Beef", "Pepper", "Garlic"]}',
 '{"steps": ["Thread meat", "Braai 10 mins"]}', 20, 20, 'easy');
```

3. Click **"Run"** (top right)
4. Wait for completion ✅

## Step 3: Get Your Credentials

1. Go to **Settings** (left sidebar)
2. Click **API**
3. Copy these keys:

### For Frontend (.env.local)
```
VITE_SUPABASE_URL = https://itkovoagalodjqfjvmlp.supabase.co
VITE_SUPABASE_ANON_KEY = [anon public key - copy from API section]
```

### For Backend (.env)
```
SUPABASE_URL = https://itkovoagalodjqfjvmlp.supabase.co
SUPABASE_KEY = [service_role key - copy from API section]
SUPABASE_JWT_SECRET = [JWT secret - copy from Project Settings → Auth]
```

## Step 4: Enable Authentication (Optional but Recommended)

1. Go to **Authentication** (left sidebar)
2. Click **Providers**
3. Enable **Email** provider
4. Configure email templates if desired

## Step 5: Test Your Database

### In Supabase Console
1. Go to **SQL Editor**
2. Run:
```sql
SELECT * FROM recipes LIMIT 5;
```

3. Should return 3 sample recipes ✅

### In Your Application
```bash
# Frontend test
curl https://spazachef.vercel.app/api/recipes

# Backend test
curl https://spazachef-api.vercel.app/api/recipes
```

## Step 6: Seed More Recipes (Optional)

Run in **SQL Editor**:
```sql
INSERT INTO recipes (title, description, category, chef_name, ingredients, instructions, prep_time_minutes, cook_time_minutes, difficulty) VALUES
('Mogodu', 'Traditional tripe stew', 'Main Courses', 'Gogo Precious', 
 '{"items": ["Tripe", "Onion", "Tomato"]}',
 '{"steps": ["Clean tripe", "Boil", "Make sauce"]}', 30, 90, 'medium'),
('Amasi & Pap', 'Sour milk with porridge', 'Breakfast', 'Chef Zama',
 '{"items": ["Maize meal", "Milk", "Salt"]}',
 '{"steps": ["Boil water", "Add maize", "Serve with amasi"]}', 10, 20, 'easy');
```

## Quick Reference

| Item | Value |
|------|-------|
| **Project ID** | itkovoagalodjqfjvmlp |
| **Project URL** | https://itkovoagalodjqfjvmlp.supabase.co |
| **Console** | https://app.supabase.com |
| **Tables** | users, recipes, recipe_favorites, subscriptions, payment_webhooks |
| **Auth** | Email provider (optional) |
| **Vector DB** | pgvector (384-dimensional) |

## Troubleshooting

### "Extension vector not found"
- Run: `CREATE EXTENSION IF NOT EXISTS vector;` in SQL Editor
- Might take a few seconds to initialize

### "Table already exists"
- Database already set up, skip to Step 3

### "Permission denied" errors
- Make sure you're using `service_role key` (not `anon` key) for backend
- Anon key is only for frontend

## What's Next?

1. ✅ Database setup complete
2. Copy credentials to `.env` files (Frontend & Backend)
3. Deploy to Vercel
4. Test end-to-end

---

**Status**: ✅ Ready for Vercel deployment
**Created**: 2026-08-07

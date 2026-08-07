# Supabase Setup Guide for SpazaChef

## Project Information
- **Project ID**: `bqffpvibvxusfxicssxz`
- **Region**: (Choose closest to SA - typically EU or US-East)
- **Database**: PostgreSQL 14+

## Step 1: Create Tables

### 1.1 Users Table
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  full_name TEXT,
  subscription_tier TEXT DEFAULT 'free' CHECK (subscription_tier IN ('free', 'basic', 'premium')),
  subscription_status TEXT DEFAULT 'inactive',
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_users_email ON users(email);
```

### 1.2 Recipes Table
```sql
CREATE TABLE recipes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  description TEXT,
  category TEXT NOT NULL,
  chef_id UUID,
  chef_name TEXT,
  ingredients JSONB,
  instructions JSONB,
  prep_time_minutes INT,
  cook_time_minutes INT,
  servings INT,
  difficulty TEXT DEFAULT 'medium',
  embedding vector(384),
  image_url TEXT,
  likes_count INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_recipes_category ON recipes(category);
CREATE INDEX idx_recipes_chef ON recipes(chef_id);
CREATE INDEX idx_recipes_embedding ON recipes USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);
```

### 1.3 Recipe Favorites Table
```sql
CREATE TABLE recipe_favorites (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  recipe_id UUID NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
  created_at TIMESTAMP DEFAULT now(),
  UNIQUE(user_id, recipe_id)
);

CREATE INDEX idx_favorites_user ON recipe_favorites(user_id);
CREATE INDEX idx_favorites_recipe ON recipe_favorites(recipe_id);
```

### 1.4 Subscriptions Table
```sql
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  tier TEXT NOT NULL CHECK (tier IN ('basic', 'premium')),
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'expired')),
  payfast_reference TEXT UNIQUE,
  ozow_reference TEXT UNIQUE,
  price_zar DECIMAL(10,2),
  renewal_date DATE,
  cancelled_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
```

### 1.5 Payment Webhooks Log Table
```sql
CREATE TABLE payment_webhooks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider TEXT NOT NULL,
  reference TEXT,
  payload JSONB,
  status TEXT,
  user_id UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_webhooks_provider ON payment_webhooks(provider);
CREATE INDEX idx_webhooks_status ON payment_webhooks(status);
```

## Step 2: Enable pgvector Extension

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## Step 3: Set Row Level Security (RLS)

### Users Table
```sql
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
  ON users
  FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON users
  FOR UPDATE
  USING (auth.uid() = id);
```

### Recipes Table
```sql
ALTER TABLE recipes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view recipes"
  ON recipes
  FOR SELECT
  USING (true);
```

### Recipe Favorites
```sql
ALTER TABLE recipe_favorites ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own favorites"
  ON recipe_favorites
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create own favorites"
  ON recipe_favorites
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own favorites"
  ON recipe_favorites
  FOR DELETE
  USING (auth.uid() = user_id);
```

### Subscriptions
```sql
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own subscription"
  ON subscriptions
  FOR SELECT
  USING (auth.uid() = user_id);
```

## Step 4: Create Functions

### Function: Update User Subscription Tier
```sql
CREATE OR REPLACE FUNCTION update_subscription_tier()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.status = 'active' THEN
    UPDATE users SET subscription_tier = NEW.tier
    WHERE id = NEW.user_id;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_subscription_tier
AFTER INSERT OR UPDATE ON subscriptions
FOR EACH ROW
EXECUTE FUNCTION update_subscription_tier();
```

### Function: Search Recipes by Embedding
```sql
CREATE OR REPLACE FUNCTION search_recipes(
  query_embedding vector(384),
  match_count INT DEFAULT 10
)
RETURNS TABLE (
  id UUID,
  title TEXT,
  description TEXT,
  similarity FLOAT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    recipes.id,
    recipes.title,
    recipes.description,
    (1 - (recipes.embedding <=> query_embedding)) as similarity
  FROM recipes
  WHERE recipes.embedding IS NOT NULL
  ORDER BY recipes.embedding <=> query_embedding
  LIMIT match_count;
END;
$$ LANGUAGE plpgsql;
```

## Step 5: Set Up Authentication

### Enable Email Provider
1. Go to **Authentication** → **Providers**
2. Enable **Email**
3. Configure email templates for signup confirmation

### Create JWT Secret
```
JWT_SECRET=your_super_secret_key_here_min_32_chars
```

## Step 6: Configure API Keys

### Get Keys from Supabase Dashboard
1. Go to **Settings** → **API**
2. Copy:
   - `Project URL`: https://bqffpvibvxusfxicssxz.supabase.co
   - `anon public key`: For frontend (public)
   - `service_role key`: For backend (keep secret!)

## Step 7: Seed Initial Data

### Insert Chef Personas
```sql
INSERT INTO recipes (title, description, category, chef_name, instructions, ingredients) VALUES
('Umqombothi', 'Traditional Zulu fermented beer', 'Beverages', 'Gogo Precious', 
 '{"steps": ["Boil grain", "Cool", "Ferment 3 days"]}', 
 '{"items": ["Maize meal", "Sorghum", "Ginger"]}'),
 
('Umngqusho', 'Cracked corn and beans stew', 'Main Courses', 'Chef Mandla',
 '{"steps": ["Cook beans", "Add corn", "Simmer 30 mins"]}',
 '{"items": ["Beans", "Corn", "Onion", "Salt"]}'),
 
('Sosaties', 'Spiced meat skewers', 'Braai', 'Boet Frik',
 '{"steps": ["Thread meat", "Season", "Braai 10 mins"]}',
 '{"items": ["Beef", "Pepper", "Garlic", "Vinegar"]}');
```

## Step 8: Monitor & Maintain

### Monitor Query Performance
```sql
-- Slow queries
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
WHERE mean_time > 100 
ORDER BY mean_time DESC;
```

### Backup Strategy
- Supabase auto-backs up daily
- Download backups weekly from **Database** → **Backups**

## Integration with Backend

Add to `backend/.env`:
```
SUPABASE_URL=https://bqffpvibvxusfxicssxz.supabase.co
SUPABASE_KEY=your_service_role_key
SUPABASE_JWT_SECRET=your_jwt_secret
DATABASE_URL=postgresql://postgres:password@db.supabase.co:5432/postgres
```

## Frontend Integration

Add to `frontend/.env.local`:
```
VITE_SUPABASE_URL=https://bqffpvibvxusfxicssxz.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_public_key
```

## Testing Queries

```bash
# Connect via psql
psql -h db.supabase.co -d postgres -U postgres

# Test vector search
SELECT * FROM search_recipes(
  (SELECT embedding FROM recipes LIMIT 1),
  10
);
```

---

**Created:** 2026-08-07
**Status:** Ready for development

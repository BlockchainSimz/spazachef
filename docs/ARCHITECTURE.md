# SpazaChef Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React 19)                       │
│              spazachef.vercel.app                            │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│               API Gateway (Vercel Edge)                      │
│          Rate Limiting | CORS | Auth Validation             │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│          FastAPI Backend                                    │
│     spazachef-api.vercel.app                                │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Routes                                                 │ │
│  │ - /api/recipes (GET, POST, PUT, DELETE)               │ │
│  │ - /api/auth (register, login, refresh)                │ │
│  │ - /api/subscriptions (plans, checkout)                │ │
│  │ - /api/webhooks/payfast (payment callbacks)           │ │
│  └──┬───────────────────────────────────────┬────────────┘ │
│     │                                        │              │
└─────┼────────────────────────────────────────┼──────────────┘
      │                                        │
      ▼                                        ▼
┌────────────────────┐            ┌──────────────────────┐
│   Supabase         │            │   Redis Cache        │
│   (PostgreSQL)     │            │ (Session/Embedding)  │
│                    │            │                      │
│ - Users            │            │ - Auth Tokens        │
│ - Recipes          │            │ - Search Results     │
│ - Subscriptions    │            │ - Rate Limit Buckets │
│ - pgvector         │            │ - Job Queue          │
│ (Embeddings)       │            │ (Celery Tasks)       │
└────────────────────┘            └──────────────────────┘
```

## Data Flow: Recipe Search

```
User Query
    │
    ▼
Frontend (React)
    │
    ▼ POST /api/recipes/search
FastAPI Endpoint
    │
    ├─ Tokenize Query
    │
    ├─ Generate Embedding
    │  (sentence-transformers)
    │
    ├─ Vector Search (pgvector)
    │  Top 20 results
    │
    ├─ Filter by Subscription
    │  (if user on free tier)
    │
    ├─ Cache Result (Redis)
    │
    └─ Return Recipes + Metadata
         │
         ▼
    Frontend Render

Cache Hit (Redis) → Direct return (< 50ms)
Cache Miss → DB Query + Cache (200-500ms)
```

## Authentication Flow

```
1. User submits credentials
                │
                ▼
2. Hash password + verify against DB
                │
                ├─ Invalid? → Return 401
                │
                └─ Valid?
                    │
                    ▼
3. Generate JWT token
   - Payload: user_id, email, subscription_tier
   - Expiry: 24 hours
   - Secret: HMAC-SHA256
                │
                ▼
4. Return token to frontend
                │
                ▼
5. Store in localStorage (frontend)
                │
                ▼
6. Attach to all API requests
   Header: Authorization: Bearer <token>
                │
                ▼
7. Middleware validates token
   - Signature check
   - Expiry check
   - User ID lookup
                │
                ├─ Invalid? → Return 401
                │
                └─ Valid? → Continue request
```

## Subscription Payment Flow

```
User selects plan
        │
        ▼
POST /api/subscriptions/checkout
        │
        ├─ Create pending subscription
        │
        └─ Redirect to PayFast
                │
                ▼
        PayFast Payment Gateway
                │
                ├─ User enters card details
                │
                ├─ Process payment
                │
                └─ Return to callback URL
                    │
                    ▼
        POST /api/webhooks/payfast
        (HMAC-MD5 validated)
                │
                ├─ Verify payment
                │
                ├─ Update subscription status
                │
                └─ Return 200 OK
                    │
                    ▼
        User subscription active
```

## Database Schema (Key Tables)

```
users
├── id (UUID, PK)
├── email (unique)
├── password_hash
├── subscription_tier (free, basic, premium)
├── created_at
└── updated_at

recipes
├── id (UUID, PK)
├── title
├── description
├── ingredients (JSONB)
├── instructions (JSONB)
├── chef_id (FK → chefs)
├── category
├── embedding (pgvector, 384-dim)
├── created_at
└── updated_at

recipe_embeddings (indexed for search)
├── recipe_id (FK → recipes)
├── embedding (pgvector)
└── created_at

subscriptions
├── id (UUID, PK)
├── user_id (FK → users)
├── tier (free, basic, premium)
├── status (active, expired, cancelled)
├── payfast_reference
├── expires_at
├── created_at
└── updated_at
```

## Caching Strategy (Redis)

| Key Pattern | TTL | Use Case |
|------------|-----|----------|
| `recipe:{id}` | 24h | Individual recipe detail |
| `search:{query_hash}` | 6h | Search results |
| `user:{id}:session` | 24h | Auth session |
| `embedding:{recipe_id}` | 7d | Recipe embeddings |
| `ratelimit:{ip}` | 1h | Rate limit bucket |
| `trending:7d` | 24h | Trending recipes |
| `chef:{id}:recipes` | 12h | Chef's recipe list |

## Deployment Architecture

### Frontend (Vercel)
- Edge functions for auth check
- Automatic deployments on `main` push
- CDN distribution
- Built-in HTTPS

### Backend (Vercel + Supabase)
- FastAPI on Vercel Functions
- Database on Supabase (hosted PostgreSQL)
- Redis on third-party provider (Upstash)
- Environment variables per environment

## Security Layers

1. **Transport**: HTTPS/TLS everywhere
2. **Authentication**: JWT tokens with HMAC-SHA256
3. **Authorization**: Role-based access control (RBAC)
4. **Webhooks**: HMAC-MD5 PayFast signature validation
5. **Rate Limiting**: IP-based bucketing (Redis)
6. **SQL Injection**: SQLAlchemy ORM parameterization
7. **CORS**: Origin whitelist


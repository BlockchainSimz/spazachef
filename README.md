# SpazaChef 🍳

**AI-powered South African recipe platform** with contextual embeddings, offline support, and POPIA compliance.

## Overview

SpazaChef connects township kitchens to African heritage recipes with an intelligent, accessible platform that works offline and respects privacy-first principles. Built for loadshedding resilience and cultural authenticity.

### Key Features

- 🧠 **Contextual AI**: Sentence-transformers embeddings for smart recipe discovery
- 📱 **Progressive Web App**: Offline-first support for loadshedding environments
- 🔐 **POPIA Compliant**: Privacy-first architecture with async JWT auth and rate limiting
- 💳 **Monetization Ready**: Subscription tiers (Free/Basic/Premium) via PayFast & Ozow
- 🔄 **Redis Caching**: Sub-second recipe retrieval and embedding lookups
- 👨‍🍳 **Chef Personas**: Gogo Precious, Chef Mandla, Tandie, Baba Thabo, Chef Zama, Boet Frik

---

## Tech Stack

### Frontend
- **Framework**: React 19 + TypeScript
- **Build**: Vite
- **Styling**: Tailwind CSS (burnt orange `#B85C2C` accent)
- **PWA**: Workbox for offline support
- **State**: React Query (data fetching), Zustand (local state)

### Backend
- **API**: FastAPI (async)
- **Database**: Supabase (PostgreSQL) - Project ID: `bqffpvibvxusfxicssxz`
- **Vector DB**: pgvector (embeddings: sentence-transformers, 384-dim)
- **Cache**: Redis (Celery async tasks)
- **Task Queue**: Celery + Redis
- **Auth**: JWT (async HMAC-MD5 validation)
- **Webhooks**: PayFast HMAC-MD5 validation

### Deployments
- **Frontend**: Vercel - `spazachef.vercel.app`
- **API**: Vercel - `spazachef-api.vercel.app`

---

## Project Structure

```
spazachef/
├── frontend/                 # React 19 + TypeScript + Vite
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/            # Route pages
│   │   ├── hooks/            # Custom React hooks
│   │   ├── services/         # API client
│   │   ├── store/            # Zustand state management
│   │   ├── types/            # TypeScript types
│   │   └── App.tsx
│   ├── public/               # Static assets
│   ├── vite.config.ts
│   └── package.json
│
├── backend/                  # FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── main.py           # FastAPI app initialization
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── api/              # Route handlers
│   │   ├── services/         # Business logic
│   │   ├── middleware/       # Auth, rate limiting, CORS
│   │   ├── security/         # JWT, PayFast webhook validation
│   │   └── config.py         # Environment config
│   ├── migrations/           # Alembic database migrations
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── docs/                     # Architecture & deployment guides
│   ├── ARCHITECTURE.md       # System design & data flow
│   ├── API.md                # API documentation
│   ├── DEPLOYMENT.md         # Vercel deployment guide
│   ├── SECURITY.md           # Security best practices
│   └── POPIA.md              # Privacy compliance
│
├── .github/
│   └── workflows/            # CI/CD pipelines
│       ├── frontend-deploy.yml
│       └── backend-deploy.yml
│
└── docker-compose.yml        # Local development
```

---

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.10+
- PostgreSQL 14+ (via Supabase)
- Redis

### Development Setup

**1. Clone & Install**
```bash
git clone https://github.com/BlockchainSimz/spazachef.git
cd spazachef

# Frontend
cd frontend && npm install && cd ..

# Backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
cd backend && pip install -r requirements.txt && cd ..
```

**2. Environment Variables**
```bash
# .env in backend/
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
REDIS_URL=redis://localhost:6379
PAYFAST_MERCHANT_ID=your_merchant_id
PAYFAST_MERCHANT_KEY=your_merchant_key
JWT_SECRET=your_secret_key
```

**3. Run Locally**
```bash
# Terminal 1: Frontend
cd frontend && npm run dev

# Terminal 2: Backend
cd backend && uvicorn app.main:app --reload

# Terminal 3: Celery worker (optional)
cd backend && celery -A app.tasks worker --loglevel=info
```

Visit: http://localhost:5173 (frontend) | http://localhost:8000 (API)

---

## Recipes & Chef Personas

### Featured Chefs
- **Gogo Precious**: Traditional Zulu cuisine & preservation
- **Chef Mandla**: Modern township fusion
- **Tandie the Baker**: Heritage breads & baked goods
- **Baba Thabo**: Street food & kasi classics
- **Chef Zama**: Health & wellness cooking
- **Boet Frik**: Braai & grilling mastery

### Recipe Categories
- Umqombothi (Traditional beverages)
- Umngqusho (Cracked corn & beans)
- Sosaties & Boerewors
- Mogodu (Tripe dishes)
- Amasi-based recipes
- Township breakfast favorites
- Heritage grains & legumes

---

## Subscription Tiers

| Tier | Price (ZAR) | Features |
|------|-----------|----------|
| **Free** | R0 | 5 recipes/day, ads, basic search |
| **Basic** | R15/month | Unlimited recipes, ad-free, offline access |
| **Premium** | R99/month | Chef consultations, custom meal plans, API access |

Payments via **PayFast** (credit card, EFT) and **Ozow** (Instant EFT)

---

## API Endpoints

### Authentication
```
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/refresh
POST   /api/auth/logout
```

### Recipes
```
GET    /api/recipes
GET    /api/recipes/{id}
POST   /api/recipes/search     # Vector similarity search
GET    /api/recipes/chef/{chef_id}
POST   /api/recipes/favorite
GET    /api/recipes/favorites
```

### Subscriptions
```
GET    /api/subscriptions/plans
POST   /api/subscriptions/checkout
POST   /api/webhooks/payfast   # PayFast webhook
GET    /api/subscriptions/status
```

### Admin
```
GET    /api/admin/recipes      # Manage recipes
POST   /api/admin/recipes
PUT    /api/admin/recipes/{id}
DELETE /api/admin/recipes/{id}
```

---

## Security

- ✅ HMAC-MD5 PayFast webhook validation
- ✅ JWT token-based auth with async validation
- ✅ Rate limiting per IP & user
- ✅ Redis-backed session management
- ✅ POPIA compliance (data minimization, consent tracking)
- ✅ CORS & CSRF protection
- ✅ SQL injection prevention via ORM

See [`docs/SECURITY.md`](docs/SECURITY.md) for details.

---

## Deployment

### Frontend (Vercel)
```bash
cd frontend
vercel deploy
```

### Backend (Vercel Functions + Supabase)
```bash
cd backend
vercel deploy
```

See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) for step-by-step guides.

---

## Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -am 'Add feature'`
4. Push: `git push origin feature/your-feature`
5. Submit a PR

---

## Testing

```bash
# Frontend
cd frontend && npm run test

# Backend
cd backend && pytest --cov=app/
```

---

## License

MIT License - See [`LICENSE`](LICENSE) for details.

---

## Support & Community

- 📧 Email: support@spazachef.dev
- 💬 Twitter/X: [@SpazaChef](https://x.com/spazachef)
- 🤝 Join our [Discord community](https://discord.gg/spazachef)

---

**Made with ❤️ in Daveyton, South Africa**

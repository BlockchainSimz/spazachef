# SpazaChef v3
React/Vite PWA + FastAPI. The recipe engine (`backend/app/engine.py`) is self-contained: no LLM or external recipe source.
Meta-learning: ratings, "I cooked this" and regenerations update Beta weights per persona and dish style (Thompson sampling); weights persist in the DB.
Run: `cd backend && pip install -r requirements.txt && uvicorn app.main:app` and `cd frontend && npm i && npm run dev`. Test: `cd backend && pytest`.
Deploy: backend on any container host with a persistent volume (SQLite); frontend on Vercel. Copy `.env.example`.

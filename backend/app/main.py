"""
SpazaChef API - FastAPI Application
AI-powered South African recipe platform
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings

# Initialize FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🍳 SpazaChef API Starting...")
    yield
    # Shutdown
    print("🍳 SpazaChef API Shutting down...")

app = FastAPI(
    title="SpazaChef API",
    description="AI-powered South African recipe platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "spazachef-api"}

# API routes (to be implemented)
@app.get("/api/v1")
async def api_root():
    return {
        "service": "SpazaChef API",
        "version": "1.0.0",
        "endpoints": {
            "recipes": "/api/v1/recipes",
            "auth": "/api/v1/auth",
            "subscriptions": "/api/v1/subscriptions",
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

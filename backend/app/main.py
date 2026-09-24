"""SpazaChef API - FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.recipes_agent import router as recipes_router
from app.config import settings

app = FastAPI(
    title="SpazaChef API",
    description="AI-powered South African recipe generator",
    version="1.2.0",
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router)
app.include_router(recipes_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "spazachef-api", "version": "1.2.0"}


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "SpazaChef API", "version": "1.2.0"}

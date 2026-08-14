"""SpazaChef API - FastAPI application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.recipes_agent import router as recipes_router
from app.config import settings

# Create FastAPI app
app = FastAPI(
    title="SpazaChef API",
    description="AI-powered South African recipe generator",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(recipes_router)

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "spazachef-api",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SpazaChef API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

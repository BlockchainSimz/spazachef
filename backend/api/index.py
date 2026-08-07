"""Vercel serverless function entry point for SpazaChef API"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.main import app as fastapi_app

# Configure CORS for Vercel deployment
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://spazachef.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Export for Vercel
app = fastapi_app

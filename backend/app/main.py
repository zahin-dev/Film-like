"""
Entry point of the Film-like API.

This module initializes the FastAPI application instance and registers
the root health check endpoint.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import auth, film, tag

# FastAPI application instance.
# This object registers all routes and is served by uvicorn.
# Metadata (title, description, version) appears in the Swagger UI at /docs.
app = FastAPI(
    title="Film-like API",
    description="Personal film diary API with TMDB integration",
    version="0.1.0"
)

# The hosted API uses the configured frontend origin. Local development
# retains the permissive default for Vite and other local clients.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(film.router)
app.include_router(tag.router)


@app.get("/")
def root():
    """
    Health check endpoint.
    Returns a simple message to confirm the API is running.
    """
    return {
        "message": "Film-like API is running"
    }

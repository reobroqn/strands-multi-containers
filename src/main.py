from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from src.api import api_router
from src.services.redis_client import RedisClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting FastAPI Agent Chat application")

    # Initialize Redis
    await RedisClient.initialize()

    yield

    # Cleanup
    await RedisClient.close()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="FastAPI Agent Chat",
    description="AI agent chat with immediate stop functionality via Redis signals",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API router
app.include_router(api_router, prefix="/api/v1")

# Static files (mount last to avoid conflicts)
app.mount("/", StaticFiles(directory="static", html=True), name="static")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    redis_ok = await RedisClient.ping()
    return {
        "status": "healthy" if redis_ok else "degraded",
        "redis": "connected" if redis_ok else "disconnected",
    }

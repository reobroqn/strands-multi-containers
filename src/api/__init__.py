# API endpoints package

from fastapi import APIRouter

from src.api import chat, stop

# Create consolidated API router
api_router = APIRouter()

# Include individual routers
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(stop.router, tags=["stop"])

"""
Aggregate router for API v1.
Import and include all endpoint routers here.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, health, items

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(items.router, prefix="/items", tags=["Items"])

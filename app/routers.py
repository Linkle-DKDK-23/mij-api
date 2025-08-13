from fastapi import APIRouter

from app.api.endpoints import (
    videos,
    users
)

api_router = APIRouter()

api_router.include_router(videos.router, prefix="/videos", tags=["Videos"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
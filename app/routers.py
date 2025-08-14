from fastapi import APIRouter

from app.api.endpoints import (
    videos,
    users,
    auth,
    creater
)

api_router = APIRouter()

api_router.include_router(videos.router, prefix="/videos", tags=["Videos"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(creater.router, prefix="/creators", tags=["Creators"])

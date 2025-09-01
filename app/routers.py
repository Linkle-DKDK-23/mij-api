from fastapi import APIRouter

from app.api.endpoints import (
    identity,
    media_assets,
    videos,
    users,
    auth,
    creater,
    gender,
    account,
    plans,
    categories,
    post,
    transcode_mc,
)

api_router = APIRouter()

api_router.include_router(videos.router, prefix="/videos", tags=["Videos"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(creater.router, prefix="/creators", tags=["Creators"])
api_router.include_router(identity.router, prefix="/identity", tags=["Identity"])
api_router.include_router(gender.router, prefix="/gender", tags=["Gender"])
api_router.include_router(account.router, prefix="/account", tags=["Account"])
api_router.include_router(media_assets.router, prefix="/media-assets", tags=["Media Assets"])
api_router.include_router(plans.router, prefix="/plans", tags=["Plans"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_router.include_router(post.router, prefix="/post", tags=["Post"])
api_router.include_router(transcode_mc.router, prefix="/transcodes", tags=["Transcode MC"])
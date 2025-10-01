from fastapi import APIRouter


# Customer routes
from app.api.endpoints.customer import (
    identity, media_assets, videos, users, auth,
    creater, gender, plans, categories, post,
    transcode_mc, top, category, ranking, social,
    purchases, preregistrations, account
)

# Admin routes
from app.api.endpoints.admin import (
    admin, admin_auth
)

# Hook routes
from app.api.hook.webhooks import router as webhooks_router

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
api_router.include_router(top.router, prefix="/top", tags=["Top"])
api_router.include_router(transcode_mc.router, prefix="/transcodes", tags=["Transcode MC"])
api_router.include_router(webhooks_router, prefix="/webhooks", tags=["Webhooks"])
api_router.include_router(category.router, prefix="/category", tags=["Category"])
api_router.include_router(ranking.router, prefix="/ranking", tags=["Ranking"])
api_router.include_router(social.router, prefix="/social", tags=["Social"])
api_router.include_router(purchases.router, prefix="/purchases", tags=["Purchases"])
api_router.include_router(preregistrations.router, prefix="/preregistrations", tags=["Preregistrations"])

# Admin routes
api_router.include_router(admin_auth.router, prefix="/admin/auth", tags=["Admin Auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
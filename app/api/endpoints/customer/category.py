from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.crud.post_crud import get_posts_by_category_slug
from app.schemas.post import PostCategoryResponse
from os import getenv
from typing import List

router = APIRouter()

BASE_URL = getenv("CDN_BASE_URL")

@router.get("/", response_model=List[PostCategoryResponse])
async def get_category_by_slug(
    slug: str = Query(..., description="Category Slug"),
    db: Session = Depends(get_db)
):
    try:
        # TODO: ランキングの返却
        posts = get_posts_by_category_slug(db, slug)
        return [PostCategoryResponse(
            id=post.Posts.id,
            description=post.Posts.description,
            thumbnail_url=f"{BASE_URL}/{post.thumbnail_key}" if post.thumbnail_key else None,
            likes_count=post.likes_count,
            creator_name=post.profile_name,
            username=post.username,
            creator_avatar_url=f"{BASE_URL}/{post.avatar_url}" if post.avatar_url else None
        ) for post in posts]
    except Exception as e:
        print("カテゴリー取得に失敗しました", e)
        raise HTTPException(status_code=500, detail=str(e))
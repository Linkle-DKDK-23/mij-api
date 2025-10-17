from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.schemas.top import (
    CategoryResponse, RankingPostResponse, CreatorResponse, PostCreatorResponse, 
    RecentPostResponse, TopPageResponse
)
from app.crud.categories_crud import get_top_categories
from app.crud.creater_crud import get_top_creators, get_new_creators
from app.crud.post_crud import get_ranking_posts, get_recent_posts
from os import getenv
from app.api.commons.utils import get_video_duration
from app.constants.enums import PostType

router = APIRouter()

BASE_URL = getenv("CDN_BASE_URL")

@router.get("/", response_model=TopPageResponse)
def get_top_page_data(db: Session = Depends(get_db)) -> TopPageResponse:
    """
    トップページ用データを取得
    """
    try:
        top_categories = get_top_categories(db, limit=8)
        ranking_posts = get_ranking_posts(db, limit=5)
        top_creators = get_top_creators(db, limit=5)
        new_creators = get_new_creators(db, limit=5)
        recent_posts = get_recent_posts(db, limit=5)
        
        return TopPageResponse(
            categories=[CategoryResponse(
                id=str(c.id), 
                name=c.name, 
                slug=c.slug, 
                post_count=c.post_count
            ) for c in top_categories],
            ranking_posts=[RankingPostResponse(
                id=str(p.Posts.id),
                post_type=p.Posts.post_type,
                title=p.Posts.description,
                thumbnail=f"{BASE_URL}/{p.thumbnail_key}" if p.thumbnail_key else None,
                likes=p.likes_count,
                duration=get_video_duration(p.duration_sec) if p.Posts.post_type == PostType.VIDEO and p.duration_sec else ("画像" if p.Posts.post_type == PostType.IMAGE else ""),
                rank=idx + 1,
                creator=PostCreatorResponse(
                    name=p.profile_name,
                    username=p.username,
                    avatar=f"{BASE_URL}/{p.avatar_url}" if p.avatar_url else None,
                    verified=False
                ),
            ) for idx, p in enumerate(ranking_posts)],
            top_creators=[CreatorResponse(
                id=str(c.Users.id),
                name=c.profile_name,
                username=c.username,
                avatar=f"{BASE_URL}/{c.avatar_url}" if c.avatar_url else None,
                followers=c.followers_count,
                rank=idx + 1
            ) for idx, c in enumerate(top_creators)],
            new_creators=[CreatorResponse(
                id=str(c.Users.id),
                name=c.profile_name,
                username=c.username,
                avatar=f"{BASE_URL}/{c.avatar_url}" if c.avatar_url else None,
                followers=0
            ) for c in new_creators],
            recent_posts=[RecentPostResponse(
                id=str(p.Posts.id),
                post_type=p.Posts.post_type,
                title=p.Posts.description,
                thumbnail=f"{BASE_URL}/{p.thumbnail_key}" if p.thumbnail_key else None,
                likes=p.likes_count or 0,
                duration=get_video_duration(p.duration_sec) if p.Posts.post_type == PostType.VIDEO and p.duration_sec else ("画像" if p.Posts.post_type == PostType.IMAGE else ""),
                creator=PostCreatorResponse(
                    name=p.profile_name,
                    username=p.username,
                    avatar=f"{BASE_URL}/{p.avatar_url}" if p.avatar_url else None,
                    verified=False
                )
            ) for p in recent_posts]
        )
    except Exception as e:
        print("トップページデータ取得エラー: ", e)
        raise HTTPException(status_code=500, detail=str(e))

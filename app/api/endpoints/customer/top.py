from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.schemas.top import (
    GenreResponse, RankingPostResponse, CreatorResponse, 
    RecentPostResponse, TopPageResponse
)
from app.crud.top_crud import (
    get_top_genres, get_ranking_posts, get_top_creators,
    get_new_creators, get_recent_posts
)
from os import getenv
from app.api.commons.utils import get_video_duration

router = APIRouter()

BASE_URL = getenv("CDN_BASE_URL")

@router.get("/", response_model=TopPageResponse)
def get_top_page_data(db: Session = Depends(get_db)) -> TopPageResponse:
    """
    トップページ用データを取得
    """
    try:
        genres = get_top_genres(db, limit=8)
        ranking_posts = get_ranking_posts(db, limit=5)
        top_creators = get_top_creators(db, limit=5)
        new_creators = get_new_creators(db, limit=5)
        recent_posts = get_recent_posts(db, limit=5)
        
        return TopPageResponse(
            genres=[GenreResponse(
                id=str(g.id), 
                name=g.name, 
                slug=g.slug, 
                post_count=g.post_count
            ) for g in genres],
            ranking_posts=[RankingPostResponse(
                id=str(p.Posts.id),
                description=p.Posts.description,
                thumbnail_url=f"{BASE_URL}/{p.thumbnail_key}" if p.thumbnail_key else None,
                likes_count=p.likes_count,
                creator_name=p.profile_name,
                username=p.username,
                creator_avatar_url=f"{BASE_URL}/{p.avatar_url}" if p.avatar_url else None,
                rank=idx + 1,
                duration=get_video_duration(p.duration_sec) if p.duration_sec else None
            ) for idx, p in enumerate(ranking_posts)],
            top_creators=[CreatorResponse(
                id=str(c.Users.id),
                name=c.profile_name,
                username=c.username,
                avatar_url=f"{BASE_URL}/{c.avatar_url}" if c.avatar_url else None,
                followers_count=c.followers_count,
                rank=idx + 1
            ) for idx, c in enumerate(top_creators)],
            new_creators=[CreatorResponse(
                id=str(c.Users.id),
                name=c.profile_name,
                username=c.username,
                avatar_url=f"{BASE_URL}/{c.avatar_url}" if c.avatar_url else None,
                followers_count=0
            ) for c in new_creators],
            recent_posts=[RecentPostResponse(
                id=str(p.Posts.id),
                description=p.Posts.description,
                thumbnail_url=f"{BASE_URL}/{p.thumbnail_key}" if p.thumbnail_key else None,
                creator_name=p.profile_name,
                username=p.username,
                creator_avatar_url=f"{BASE_URL}/{p.avatar_url}" if p.avatar_url else None,
                duration=get_video_duration(p.duration_sec) if p.duration_sec else None,
                likes_count=p.likes_count or 0
            ) for p in recent_posts]
        )
    except Exception as e:
        print("トップページデータ取得エラー: ", e)
        raise HTTPException(status_code=500, detail=str(e))

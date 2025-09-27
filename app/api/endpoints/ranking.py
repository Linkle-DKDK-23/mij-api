from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.crud.ranking_crud import (
    get_ranking_posts_all_time,
    get_ranking_posts_monthly,
    get_ranking_posts_weekly,
    get_ranking_posts_daily
)
from app.schemas.ranking import (
    RankingPostsAllTimeResponse,
    RankingPostsMonthlyResponse,
    RankingPostsWeeklyResponse,
    RankingPostsDailyResponse,
    RankingResponse
)
from os import getenv

BASE_URL = getenv("CDN_BASE_URL")

router = APIRouter()

@router.get("/")
async def get_ranking(
    db: Session = Depends(get_db),
):
    try:
        ranking_posts_all_time = get_ranking_posts_all_time(db, limit=50)
        ranking_posts_monthly = get_ranking_posts_monthly(db, limit=50)
        ranking_posts_weekly = get_ranking_posts_weekly(db, limit=50)
        ranking_posts_daily = get_ranking_posts_daily(db, limit=50)

        return RankingResponse(
            all_time=[RankingPostsAllTimeResponse(
                id=str(post.Posts.id),  # UUIDを文字列に変換
                description=post.Posts.description,
                thumbnail_url=f"{BASE_URL}/{post.thumbnail_key}" if post.thumbnail_key else None,
                likes_count=post.likes_count,
                creator_name=post.slug,
                display_name=post.display_name,
                creator_avatar_url=f"{BASE_URL}/{post.avatar_url}" if post.avatar_url else None,
                rank=idx + 1
            ) for idx, post in enumerate(ranking_posts_all_time)],
            monthly=[RankingPostsMonthlyResponse(
                id=str(post.Posts.id),  # UUIDを文字列に変換
                description=post.Posts.description,
                thumbnail_url=f"{BASE_URL}/{post.thumbnail_key}" if post.thumbnail_key else None,
                likes_count=post.likes_count,
                creator_name=post.slug,
                display_name=post.display_name,
                creator_avatar_url=f"{BASE_URL}/{post.avatar_url}" if post.avatar_url else None,
                rank=idx + 1
            ) for idx, post in enumerate(ranking_posts_monthly)],
            weekly=[RankingPostsWeeklyResponse(
                id=str(post.Posts.id),  # UUIDを文字列に変換
                description=post.Posts.description,
                thumbnail_url=f"{BASE_URL}/{post.thumbnail_key}" if post.thumbnail_key else None,
                likes_count=post.likes_count,
                creator_name=post.slug,
                display_name=post.display_name,
                creator_avatar_url=f"{BASE_URL}/{post.avatar_url}" if post.avatar_url else None,
                rank=idx + 1
            ) for idx, post in enumerate(ranking_posts_weekly)],
            daily=[RankingPostsDailyResponse(
                id=str(post.Posts.id),  # UUIDを文字列に変換
                description=post.Posts.description,
                thumbnail_url=f"{BASE_URL}/{post.thumbnail_key}" if post.thumbnail_key else None,
                likes_count=post.likes_count,
                creator_name=post.slug,
                display_name=post.display_name,
                creator_avatar_url=f"{BASE_URL}/{post.avatar_url}" if post.avatar_url else None,
                rank=idx + 1
            ) for idx, post in enumerate(ranking_posts_daily)],
        )


    except Exception as e:
        print('エラーが発生しました', e)
        raise HTTPException(status_code=500, detail=str(e))
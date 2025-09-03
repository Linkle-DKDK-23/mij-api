from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.db.base import get_db
from app.models.categories import Categories
from app.models.post_categories import PostCategories
from app.models.posts import Posts
from app.models.social import Likes, Follows
from app.models.user import Users
from app.models.profiles import Profiles
from app.models.media_assets import MediaAssets
from app.schemas.top import (
    GenreResponse, RankingPostResponse, CreatorResponse, 
    RecentPostResponse, TopPageResponse
)
from app.constants.enums import AccountType

router = APIRouter()

@router.get("/", response_model=TopPageResponse)
def get_top_page_data(db: Session = Depends(get_db)):
    """
    トップページ用データを取得
    """
    try:
        genres = (
            db.query(
                Categories.id,
                Categories.name,
                func.count(PostCategories.post_id).label('post_count')
            )
            .join(PostCategories, Categories.id == PostCategories.category_id)
            .group_by(Categories.id, Categories.name)
            .order_by(desc('post_count'))
            .limit(8)
            .all()
        )
        
        ranking_posts = (
            db.query(
                Posts,
                func.count(Likes.post_id).label('likes_count'),
                Profiles.display_name,
                Profiles.avatar_url,
                MediaAssets.storage_key.label('thumbnail_key')
            )
            .join(Likes, Posts.id == Likes.post_id)
            .join(Users, Posts.creator_user_id == Users.id)
            .join(Profiles, Users.id == Profiles.user_id)
            .outerjoin(MediaAssets, (Posts.id == MediaAssets.post_id) & (MediaAssets.status == 2))
            .group_by(Posts.id, Profiles.display_name, Profiles.avatar_url, MediaAssets.storage_key)
            .order_by(desc('likes_count'))
            .limit(5)
            .all()
        )
        
        top_creators = (
            db.query(
                Users,
                Profiles.display_name,
                Profiles.avatar_url,
                func.count(Follows.creator_user_id).label('followers_count')
            )
            .join(Profiles, Users.id == Profiles.user_id)
            .join(Follows, Users.id == Follows.creator_user_id)
            .filter(Users.role == AccountType.CREATOR)
            .group_by(Users.id, Profiles.display_name, Profiles.avatar_url)
            .order_by(desc('followers_count'))
            .limit(5)
            .all()
        )
        
        new_creators = (
            db.query(Users, Profiles.display_name, Profiles.avatar_url)
            .join(Profiles, Users.id == Profiles.user_id)
            .filter(Users.role == AccountType.CREATOR)
            .order_by(desc(Users.created_at))
            .limit(5)
            .all()
        )
        
        recent_posts = (
            db.query(
                Posts,
                Profiles.display_name,
                Profiles.avatar_url,
                MediaAssets.storage_key.label('thumbnail_key')
            )
            .join(Users, Posts.creator_user_id == Users.id)
            .join(Profiles, Users.id == Profiles.user_id)
            .outerjoin(MediaAssets, (Posts.id == MediaAssets.post_id) & (MediaAssets.status == 2))
            .order_by(desc(Posts.created_at))
            .limit(5)
            .all()
        )
        
        return TopPageResponse(
            genres=[GenreResponse(id=str(g.id), name=g.name, post_count=g.post_count) for g in genres],
            ranking_posts=[RankingPostResponse(
                id=str(p.Posts.id),
                description=p.Posts.description,
                thumbnail_url=f"https://cdn-dev.mijfans.jp/{p.thumbnail_key}" if p.thumbnail_key else None,
                likes_count=p.likes_count,
                creator_name=p.display_name,
                creator_avatar_url=f"https://cdn-dev.mijfans.jp/{p.avatar_url}" if p.avatar_url else None,
                rank=idx + 1
            ) for idx, p in enumerate(ranking_posts)],
            top_creators=[CreatorResponse(
                id=str(c.Users.id),
                name=c.display_name,
                avatar_url=f"https://cdn-dev.mijfans.jp/{c.avatar_url}" if c.avatar_url else None,
                followers_count=c.followers_count,
                rank=idx + 1
            ) for idx, c in enumerate(top_creators)],
            new_creators=[CreatorResponse(
                id=str(c.Users.id),
                name=c.display_name,
                avatar_url=f"https://cdn-dev.mijfans.jp/{c.avatar_url}" if c.avatar_url else None,
                followers_count=0
            ) for c in new_creators],
            recent_posts=[RecentPostResponse(
                id=str(p.Posts.id),
                description=p.Posts.description,
                thumbnail_url=f"https://cdn-dev.mijfans.jp/{p.thumbnail_key}" if p.thumbnail_key else None,
                creator_name=p.display_name,
                creator_avatar_url=f"https://cdn-dev.mijfans.jp/{p.avatar_url}" if p.avatar_url else None
            ) for p in recent_posts]
        )
    except Exception as e:
        print("トップページデータ取得エラー: ", e)
        raise HTTPException(status_code=500, detail=str(e))

from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from app.models.posts import Posts
from app.models.user import Users
from app.models.profiles import Profiles
from app.models.media_assets import MediaAssets
from app.models.social import Likes
from app.constants.enums import MediaAssetKind, PostStatus

def get_ranking_posts_all_time(db: Session, limit: int = 500):
    """
    全期間でいいね数が多い投稿を取得
    """
    return (
        db.query(
            Posts,
            func.count(Likes.post_id).label('likes_count'),
            Users.slug,
            Profiles.display_name,
            Profiles.avatar_url,
            MediaAssets.storage_key.label('thumbnail_key')
        )
        .join(Users, Posts.creator_user_id == Users.id)
        .join(Profiles, Users.id == Profiles.user_id)
        .outerjoin(MediaAssets, (Posts.id == MediaAssets.post_id) & (MediaAssets.kind == MediaAssetKind.THUMBNAIL))
        .outerjoin(Likes, Posts.id == Likes.post_id)
        # TODO: 公開済みの投稿のみにする
        # .filter(Posts.status == PostStatus.APPROVED)  # 公開済みの投稿のみ
        .filter(Posts.deleted_at.is_(None))  # 削除されていない投稿のみ
        .group_by(Posts.id, Users.slug, Profiles.display_name, Profiles.avatar_url, MediaAssets.storage_key)
        .order_by(desc('likes_count'))
        .limit(limit)
        .all()
    )


def get_ranking_posts_monthly(db: Session, limit: int = 50):
    """
    月間でいいね数が多い投稿を取得
    """
    one_month_ago = datetime.now() - timedelta(days=30)
    
    return (
        db.query(
            Posts,
            func.count(Likes.post_id).label('likes_count'),
            Users.slug,
            Profiles.display_name,
            Profiles.avatar_url,
            MediaAssets.storage_key.label('thumbnail_key')
        )
        .join(Users, Posts.creator_user_id == Users.id)
        .join(Profiles, Users.id == Profiles.user_id)
        .outerjoin(MediaAssets, (Posts.id == MediaAssets.post_id) & (MediaAssets.kind == MediaAssetKind.THUMBNAIL))
        .outerjoin(Likes, Posts.id == Likes.post_id)
        # .filter(Posts.status == PostStatus.APPROVED)
        .filter(Posts.deleted_at.is_(None))
        .filter(Posts.created_at >= one_month_ago)  # 過去30日以内のいいね
        .group_by(Posts.id, Users.slug, Profiles.display_name, Profiles.avatar_url, MediaAssets.storage_key)
        .order_by(desc('likes_count'))
        .limit(limit)
        .all()
    )


def get_ranking_posts_weekly(db: Session, limit: int = 50):
    """
    週間でいいね数が多い投稿を取得
    """
    one_week_ago = datetime.now() - timedelta(days=7)
    
    return (
        db.query(
            Posts,
            func.count(Likes.post_id).label('likes_count'),
            Users.slug,
            Profiles.display_name,
            Profiles.avatar_url,
            MediaAssets.storage_key.label('thumbnail_key')
        )
        .join(Users, Posts.creator_user_id == Users.id)
        .join(Profiles, Users.id == Profiles.user_id)
        .outerjoin(MediaAssets, (Posts.id == MediaAssets.post_id) & (MediaAssets.kind == MediaAssetKind.THUMBNAIL))
        .outerjoin(Likes, Posts.id == Likes.post_id)
        # .filter(Posts.status == PostStatus.APPROVED)
        .filter(Posts.deleted_at.is_(None))
        .filter(Posts.created_at >= one_week_ago)  # 過去7日以内のいいね
        .group_by(Posts.id, Users.slug, Profiles.display_name, Profiles.avatar_url, MediaAssets.storage_key)
        .order_by(desc('likes_count'))
        .limit(limit)
        .all()
    )


def get_ranking_posts_daily(db: Session, limit: int = 50):
    """
    日間でいいね数が多い投稿を取得
    """
    one_day_ago = datetime.now() - timedelta(days=1)
    
    return (
        db.query(
            Posts,
            func.count(Likes.post_id).label('likes_count'),
            Users.slug,
            Profiles.display_name,
            Profiles.avatar_url,
            MediaAssets.storage_key.label('thumbnail_key')
        )
        .join(Users, Posts.creator_user_id == Users.id)
        .join(Profiles, Users.id == Profiles.user_id)
        .outerjoin(MediaAssets, (Posts.id == MediaAssets.post_id) & (MediaAssets.kind == MediaAssetKind.THUMBNAIL))
        .outerjoin(Likes, Posts.id == Likes.post_id)
        # .filter(Posts.status == PostStatus.APPROVED)
        .filter(Posts.deleted_at.is_(None))
        .filter(Posts.created_at >= one_day_ago)  # 過去1日以内のいいね
        .group_by(Posts.id, Users.slug, Profiles.display_name, Profiles.avatar_url, MediaAssets.storage_key)
        .order_by(desc('likes_count'))
        .limit(limit)
        .all()
    )
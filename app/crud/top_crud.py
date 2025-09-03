from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.categories import Categories
from app.models.post_categories import PostCategories
from app.models.posts import Posts
from app.models.social import Likes, Follows
from app.models.user import Users
from app.models.profiles import Profiles
from app.models.media_assets import MediaAssets
from app.constants.enums import AccountType


def get_top_genres(db: Session, limit: int = 8):
    """
    投稿数上位のカテゴリを取得
    """
    return (
        db.query(
            Categories.id,
            Categories.name,
            func.count(PostCategories.post_id).label('post_count')
        )
        .join(PostCategories, Categories.id == PostCategories.category_id)
        .group_by(Categories.id, Categories.name)
        .order_by(desc('post_count'))
        .limit(limit)
        .all()
    )


def get_ranking_posts(db: Session, limit: int = 5):
    """
    いいね数上位の投稿を取得
    """
    return (
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
        .outerjoin(MediaAssets, (Posts.id == MediaAssets.post_id) & (MediaAssets.kind == 2))
        .group_by(Posts.id, Profiles.display_name, Profiles.avatar_url, MediaAssets.storage_key)
        .order_by(desc('likes_count'))
        .limit(limit)
        .all()
    )


def get_top_creators(db: Session, limit: int = 5):
    """
    フォロワー数上位のクリエイターを取得
    """
    return (
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
        .limit(limit)
        .all()
    )


def get_new_creators(db: Session, limit: int = 5):
    """
    登録順最新のクリエイターを取得
    """
    return (
        db.query(Users, Profiles.display_name, Profiles.avatar_url)
        .join(Profiles, Users.id == Profiles.user_id)
        .filter(Users.role == AccountType.CREATOR)
        .order_by(desc(Users.created_at))
        .limit(limit)
        .all()
    )


def get_recent_posts(db: Session, limit: int = 5):
    """
    最新の投稿を取得
    """
    return (
        db.query(
            Posts,
            Profiles.display_name,
            Profiles.avatar_url,
            MediaAssets.storage_key.label('thumbnail_key')
        )
        .join(Users, Posts.creator_user_id == Users.id)
        .join(Profiles, Users.id == Profiles.user_id)
        .outerjoin(MediaAssets, (Posts.id == MediaAssets.post_id) & (MediaAssets.kind == 2))
        .order_by(desc(Posts.created_at))
        .limit(limit)
        .all()
    )

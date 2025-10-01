from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, desc
from app.models.categories import Categories
from app.models.post_categories import PostCategories
from app.models.posts import Posts
from app.models.social import Likes, Follows
from app.models.user import Users
from app.models.profiles import Profiles
from app.models.media_assets import MediaAssets
from app.models.media_renditions import MediaRenditions
from app.constants.enums import AccountType, MediaAssetKind, PostStatus

# エイリアスを定義
ThumbnailAssets = aliased(MediaAssets)
VideoAssets = aliased(MediaAssets)

def get_top_genres(db: Session, limit: int = 8):
    """
    投稿数上位のカテゴリを取得
    """
    return (
        db.query(
            Categories.id,
            Categories.name,
            Categories.slug,
            func.count(PostCategories.post_id).label('post_count')
        )
        .join(PostCategories, Categories.id == PostCategories.category_id)
        .group_by(Categories.id, Categories.name, Categories.slug)
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
            Users.profile_name,
            Profiles.username,
            Profiles.avatar_url,
            ThumbnailAssets.storage_key.label('thumbnail_key'),
            MediaRenditions.duration_sec.label('duration_sec')
        )
        .outerjoin(Likes, Posts.id == Likes.post_id)
        .join(Users, Posts.creator_user_id == Users.id)
        .join(Profiles, Users.id == Profiles.user_id)
        # サムネイル用のMediaAssets（kind=2）
        .outerjoin(ThumbnailAssets, (Posts.id == ThumbnailAssets.post_id) & (ThumbnailAssets.kind == MediaAssetKind.THUMBNAIL))
        # メインビデオ用のMediaAssets（kind=4）
        .outerjoin(VideoAssets, (Posts.id == VideoAssets.post_id) & (VideoAssets.kind == MediaAssetKind.MAIN_VIDEO))
        # メインビデオのMediaRenditions
        .outerjoin(MediaRenditions, VideoAssets.id == MediaRenditions.asset_id)
        .filter(Posts.status == PostStatus.APPROVED)
        .group_by(
            Posts.id, 
            Users.profile_name,
            Profiles.username, 
            Profiles.avatar_url, 
            ThumbnailAssets.storage_key, 
            MediaRenditions.duration_sec
        )
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
            Users.profile_name,
            Profiles.username,
            Profiles.avatar_url,
            func.count(Follows.creator_user_id).label('followers_count')
        )
        .join(Profiles, Users.id == Profiles.user_id)
        .outerjoin(Follows, Users.id == Follows.creator_user_id)
        .filter(Users.role == AccountType.CREATOR)
        .group_by(Users.id, Users.profile_name, Profiles.username, Profiles.avatar_url)
        .order_by(desc('followers_count'))
        .limit(limit)
        .all()
    )


def get_new_creators(db: Session, limit: int = 5):
    """
    登録順最新のクリエイターを取得
    """
    return (
        db.query(
            Users, 
            Users.profile_name,
            Profiles.username,
            Profiles.avatar_url
        )
        .join(Profiles, Users.id == Profiles.user_id)
        .filter(Users.role == AccountType.CREATOR)
        .order_by(desc(Users.created_at))
        .limit(limit)
        .all()
    )


def get_recent_posts(db: Session, limit: int = 50):
    """
    最新の投稿を取得（いいね数も含む）
    """
    return (
        db.query(
            Posts,
            Users.profile_name,
            Profiles.username,
            Profiles.avatar_url,
            ThumbnailAssets.storage_key.label('thumbnail_key'),
            MediaRenditions.duration_sec.label('duration_sec'),
            func.count(Likes.post_id).label('likes_count')
        )
        .join(Users, Posts.creator_user_id == Users.id)
        .join(Profiles, Users.id == Profiles.user_id)
        # サムネイル用のMediaAssets（kind=2）
        .outerjoin(ThumbnailAssets, (Posts.id == ThumbnailAssets.post_id) & (ThumbnailAssets.kind == MediaAssetKind.THUMBNAIL))
        # メインビデオ用のMediaAssets（kind=4）
        .outerjoin(VideoAssets, (Posts.id == VideoAssets.post_id) & (VideoAssets.kind == MediaAssetKind.MAIN_VIDEO))
        # メインビデオのMediaRenditions
        .outerjoin(MediaRenditions, VideoAssets.id == MediaRenditions.asset_id)
        # いいね数を取得するためのLikesテーブル
        .outerjoin(Likes, Posts.id == Likes.post_id)
        .filter(Posts.status == PostStatus.APPROVED)
        .group_by(
            Posts.id,
            Users.profile_name,
            Profiles.username,
            Profiles.avatar_url,
            ThumbnailAssets.storage_key,
            MediaRenditions.duration_sec
        )
        .order_by(desc(Posts.created_at))
        .limit(limit)
        .all()
    )

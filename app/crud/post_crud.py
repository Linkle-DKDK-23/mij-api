from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.posts import Posts
from app.models.social import Likes
from uuid import UUID
from datetime import datetime
from app.constants.enums import PostStatus, MediaAssetKind
from app.schemas.post import PostCreateRequest
from app.models.post_categories import PostCategories
from app.models.categories import Categories
from typing import List
from app.models.user import Users
from app.models.profiles import Profiles
from app.models.media_assets import MediaAssets
from app.models.plans import Plans, PostPlans   
from app.models.prices import Prices

def get_total_likes_by_user_id(db: Session, user_id: UUID) -> int:
    """
    ユーザーの投稿についた総合いいね数を取得
    """
    
    # いいねテーブルと結合していいね数を取得
    total_likes = (
        db.query(func.count(Likes.post_id))
        .join(Posts, Likes.post_id == Posts.id)
        .filter(Posts.creator_user_id == user_id)
        .filter(Posts.deleted_at.is_(None))  # 削除されていない投稿のみ
        .scalar()
    )
    
    return total_likes or 0

def get_posts_count_by_user_id(db: Session, user_id: UUID) -> dict:
    """
    各ステータスの投稿数を取得
    """
    
    # 審査中
    peding_posts_count = db.query(Posts).filter(Posts.creator_user_id == user_id).filter(Posts.deleted_at.is_(None)).filter(Posts.status == PostStatus.PENDING).count()

    # 修正
    rejected_posts_count = db.query(Posts).filter(Posts.creator_user_id == user_id).filter(Posts.deleted_at.is_(None)).filter(Posts.status == PostStatus.REJECTED).count()

    # 非公開
    unpublished_posts_count = db.query(Posts).filter(Posts.creator_user_id == user_id).filter(Posts.deleted_at.is_(None)).filter(Posts.status == PostStatus.UNPUBLISHED).count()

    # 削除
    deleted_posts_count = db.query(Posts).filter(Posts.creator_user_id == user_id).filter(Posts.deleted_at.is_(None)).filter(Posts.status == PostStatus.DELETED).count()

    # 公開
    approved_posts_count = db.query(Posts).filter(Posts.creator_user_id == user_id).filter(Posts.deleted_at.is_(None)).filter(Posts.status == PostStatus.APPROVED).count()

    return {
        "peding_posts_count": peding_posts_count,
        "rejected_posts_count": rejected_posts_count,
        "unpublished_posts_count": unpublished_posts_count,
        "deleted_posts_count": deleted_posts_count,
        "approved_posts_count": approved_posts_count
    }

def create_post(db: Session, post_data: dict):
    """
    投稿を作成
    """
    post = Posts(**post_data)
    db.add(post)
    db.flush()
    return post

def update_post_media_assets(db: Session, post_id: UUID, key: str, kind: str):
    """
    投稿のメディアアセットを更新
    """
    post = db.query(Posts).filter(Posts.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # kindを整数値にマッピング
    kind_mapping = {
        "ogp": MediaAssetKind.OGP,
        "thumbnail": MediaAssetKind.THUMBNAIL,
        "main": MediaAssetKind.MAIN_VIDEO,
        "sample": MediaAssetKind.SAMPLE_VIDEO,
        "images": MediaAssetKind.IMAGES,
    }
    
    kind_int = kind_mapping.get(kind)
    if kind_int is None:
        raise HTTPException(status_code=400, detail=f"Unsupported kind: {kind}")

    post.updated_at = datetime.now()
    db.add(post)
    db.flush()
    return post

def update_post_status(db: Session, post_id: UUID, status: int):
    """
    投稿のステータスを更新
    """
    post = db.query(Posts).filter(Posts.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post.status = status
    post.updated_at = datetime.now()
    db.add(post)
    db.flush()
    return post

def get_posts_by_category_slug(db: Session, slug: str) -> List[Posts]:
    """
    カテゴリーに紐づく投稿を取得
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
        .join(PostCategories, Posts.id == PostCategories.post_id)
        .join(Categories, PostCategories.category_id == Categories.id)
        .join(Users, Posts.creator_user_id == Users.id)
        .join(Profiles, Users.id == Profiles.user_id)
        .outerjoin(MediaAssets, (Posts.id == MediaAssets.post_id) & (MediaAssets.kind == MediaAssetKind.THUMBNAIL))
        .outerjoin(Likes, Posts.id == Likes.post_id)
        .filter(Categories.slug == slug)
        .group_by(Posts.id, Users.slug, Profiles.display_name, Profiles.avatar_url, MediaAssets.storage_key)
        .order_by(desc(Posts.created_at))
        .all()
    )

def get_post_status_by_user_id(db: Session, user_id: UUID) -> dict:
    """
    ユーザーの投稿ステータスを取得
    """
    
    # 審査中の投稿を取得
    pending_posts = (
        db.query(
            Posts,
            func.count(Likes.post_id).label('likes_count'),
            Users.slug,
            Profiles.display_name,
            Profiles.avatar_url,
            func.min(Prices.price).label('post_price'),  # 最安値を取得
            func.min(Prices.currency).label('post_currency'),  # 最安値の通貨を取得
            MediaAssets.storage_key.label('thumbnail_key')
        )
        .join(Users, Posts.creator_user_id == Users.id)
        .join(Profiles, Users.id == Profiles.user_id)
        .outerjoin(MediaAssets, (Posts.id == MediaAssets.post_id) & (MediaAssets.kind == MediaAssetKind.THUMBNAIL))
        .outerjoin(Likes, Posts.id == Likes.post_id)
        .outerjoin(PostPlans, Posts.id == PostPlans.post_id)
        .outerjoin(Plans, PostPlans.plan_id == Plans.id)
        .outerjoin(Prices, Plans.id == Prices.plan_id)
        .filter(Posts.creator_user_id == user_id)
        .filter(Posts.deleted_at.is_(None))
        .filter(Posts.status == PostStatus.PENDING)
        .group_by(Posts.id, Users.slug, Profiles.display_name, Profiles.avatar_url, MediaAssets.storage_key)
        .order_by(desc(Posts.created_at))
        .all()
    )

    # 拒否された投稿を取得
    rejected_posts = (
        db.query(
            Posts,
            func.count(Likes.post_id).label('likes_count'),
            Users.slug,
            Profiles.display_name,
            Profiles.avatar_url,
            func.min(Prices.price).label('post_price'),  # 最安値を取得
            func.min(Prices.currency).label('post_currency'),  # 最安値の通貨を取得
            MediaAssets.storage_key.label('thumbnail_key')
        )
        .join(Users, Posts.creator_user_id == Users.id)
        .join(Profiles, Users.id == Profiles.user_id)
        .outerjoin(MediaAssets, (Posts.id == MediaAssets.post_id) & (MediaAssets.kind == MediaAssetKind.THUMBNAIL))
        .outerjoin(Likes, Posts.id == Likes.post_id)
        .outerjoin(PostPlans, Posts.id == PostPlans.post_id)
        .outerjoin(Plans, PostPlans.plan_id == Plans.id)
        .outerjoin(Prices, Plans.id == Prices.plan_id)
        .filter(Posts.creator_user_id == user_id)
        .filter(Posts.deleted_at.is_(None))
        .filter(Posts.status == PostStatus.REJECTED)
        .group_by(Posts.id, Users.slug, Profiles.display_name, Profiles.avatar_url, MediaAssets.storage_key)
        .order_by(desc(Posts.created_at))
        .all()
    )

    # 非公開の投稿を取得
    unpublished_posts = (
        db.query(
            Posts,
            func.count(Likes.post_id).label('likes_count'),
            Users.slug,
            Profiles.display_name,
            Profiles.avatar_url,
            func.min(Prices.price).label('post_price'),  # 最安値を取得
            func.min(Prices.currency).label('post_currency'),  # 最安値の通貨を取得
            MediaAssets.storage_key.label('thumbnail_key')
        )
        .join(Users, Posts.creator_user_id == Users.id)
        .join(Profiles, Users.id == Profiles.user_id)
        .outerjoin(MediaAssets, (Posts.id == MediaAssets.post_id) & (MediaAssets.kind == MediaAssetKind.THUMBNAIL))
        .outerjoin(Likes, Posts.id == Likes.post_id)
        .outerjoin(PostPlans, Posts.id == PostPlans.post_id)
        .outerjoin(Plans, PostPlans.plan_id == Plans.id)
        .outerjoin(Prices, Plans.id == Prices.plan_id)
        .filter(Posts.creator_user_id == user_id)
        .filter(Posts.deleted_at.is_(None))
        .filter(Posts.status == PostStatus.UNPUBLISHED)
        .group_by(Posts.id, Users.slug, Profiles.display_name, Profiles.avatar_url, MediaAssets.storage_key)
        .order_by(desc(Posts.created_at))
        .all()
    )

    # 削除された投稿を取得
    deleted_posts = (
        db.query(
            Posts,
            func.count(Likes.post_id).label('likes_count'),
            Users.slug,
            Profiles.display_name,
            Profiles.avatar_url,
            func.min(Prices.price).label('post_price'),  # 最安値を取得
            func.min(Prices.currency).label('post_currency'),  # 最安値の通貨を取得
            MediaAssets.storage_key.label('thumbnail_key')
        )
        .join(Users, Posts.creator_user_id == Users.id)
        .join(Profiles, Users.id == Profiles.user_id)
        .outerjoin(MediaAssets, (Posts.id == MediaAssets.post_id) & (MediaAssets.kind == MediaAssetKind.THUMBNAIL))
        .outerjoin(Likes, Posts.id == Likes.post_id)
        .outerjoin(PostPlans, Posts.id == PostPlans.post_id)
        .outerjoin(Plans, PostPlans.plan_id == Plans.id)
        .outerjoin(Prices, Plans.id == Prices.plan_id)
        .filter(Posts.creator_user_id == user_id)
        .filter(Posts.deleted_at.is_(None))
        .filter(Posts.status == PostStatus.DELETED)
        .group_by(Posts.id, Users.slug, Profiles.display_name, Profiles.avatar_url, MediaAssets.storage_key)
        .order_by(desc(Posts.created_at))
        .all()
    )

    # 公開された投稿を取得
    approved_posts = (
        db.query(
            Posts,
            func.count(Likes.post_id).label('likes_count'),
            Users.slug,
            Profiles.display_name,
            Profiles.avatar_url,
            func.min(Prices.price).label('post_price'),  # 最安値を取得
            func.min(Prices.currency).label('post_currency'),  # 最安値の通貨を取得
            MediaAssets.storage_key.label('thumbnail_key')
        )
        .join(Users, Posts.creator_user_id == Users.id)
        .join(Profiles, Users.id == Profiles.user_id)
        .outerjoin(MediaAssets, (Posts.id == MediaAssets.post_id) & (MediaAssets.kind == MediaAssetKind.THUMBNAIL))
        .outerjoin(Likes, Posts.id == Likes.post_id)
        .outerjoin(PostPlans, Posts.id == PostPlans.post_id)
        .outerjoin(Plans, PostPlans.plan_id == Plans.id)
        .outerjoin(Prices, Plans.id == Prices.plan_id)
        .filter(Posts.creator_user_id == user_id)
        .filter(Posts.deleted_at.is_(None))
        .filter(Posts.status == PostStatus.APPROVED)
        .group_by(Posts.id, Users.slug, Profiles.display_name, Profiles.avatar_url, MediaAssets.storage_key)
        .order_by(desc(Posts.created_at))
        .all()
    )

    return {
        "pending_posts": pending_posts,
        "rejected_posts": rejected_posts,
        "unpublished_posts": unpublished_posts,
        "deleted_posts": deleted_posts,
        "approved_posts": approved_posts
    }
    
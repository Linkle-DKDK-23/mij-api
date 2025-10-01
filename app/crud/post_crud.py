from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, exists
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
from app.models.media_renditions import MediaRenditions
from app.api.commons.utils import get_video_duration
from app.constants.enums import PlanStatus
from app.models.purchases import Purchases

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
            Users.profile_name,
            Profiles.username,
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
        .group_by(Posts.id, Users.profile_name, Profiles.username, Profiles.avatar_url, MediaAssets.storage_key)
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
            Users.profile_name,
            Profiles.username,
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
        .group_by(Posts.id, Users.profile_name, Profiles.username, Profiles.avatar_url, MediaAssets.storage_key)
        .order_by(desc(Posts.created_at))
        .all()
    )

    # 拒否された投稿を取得
    rejected_posts = (
        db.query(
            Posts,
            func.count(Likes.post_id).label('likes_count'),
            Users.profile_name,
            Profiles.username,
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
        .group_by(Posts.id, Users.profile_name, Profiles.username, Profiles.avatar_url, MediaAssets.storage_key)
        .order_by(desc(Posts.created_at))
        .all()
    )

    # 非公開の投稿を取得
    unpublished_posts = (
        db.query(
            Posts,
            func.count(Likes.post_id).label('likes_count'),
            Users.profile_name,
            Profiles.username,
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
        .group_by(Posts.id, Users.profile_name, Profiles.username, Profiles.avatar_url, MediaAssets.storage_key)
        .order_by(desc(Posts.created_at))
        .all()
    )

    # 削除された投稿を取得
    deleted_posts = (
        db.query(
            Posts,
            func.count(Likes.post_id).label('likes_count'),
            Users.profile_name,
            Profiles.username,
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
        .group_by(Posts.id, Users.profile_name, Profiles.username, Profiles.avatar_url, MediaAssets.storage_key)
        .order_by(desc(Posts.created_at))
        .all()
    )

    # 公開された投稿を取得
    approved_posts = (
        db.query(
            Posts,
            func.count(Likes.post_id).label('likes_count'),
            Users.profile_name,
            Profiles.username,
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
        .group_by(Posts.id, Users.profile_name, Profiles.username, Profiles.avatar_url, MediaAssets.storage_key)
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

def get_post_detail_by_id(db: Session, post_id: str, user_id: str | None) -> dict:
    """
    投稿詳細を取得（メディア情報とクリエイター情報、カテゴリ情報、販売情報を含む）
    """
    # 投稿とクリエイター情報を取得
    post, creator, creator_profile = _get_post_and_creator_info(db, post_id)
    if not post:
        return None
    
    # 各種情報を取得
    categories = _get_post_categories(db, post_id)
    likes_count = _get_likes_count(db, post_id)
    sale_info = _get_sale_info(db, post_id)
    media_info = _get_media_info(db, post_id, user_id)
    
    # 結果を統合して返却
    return {
        "post": post,
        "creator": creator,
        "creator_profile": creator_profile,
        "categories": categories,
        "likes_count": likes_count,
        **sale_info,
        **media_info
    }
    
def _is_purchased(db: Session, user_id: UUID | None, post_id: UUID) -> bool:
    """
    ユーザーが投稿を購入しているかどうかを判定

    Args:
        db (Session): データベースセッション
        user_id (UUID | None): ユーザーID（Noneの場合は未購入扱い）
        post_id (UUID): 投稿ID

    Returns:
        bool: 購入済みの場合True、未購入の場合False
    """
    if user_id is None:
        return False
    return db.query(exists().where(
        Purchases.user_id == user_id,
        Purchases.post_id == post_id,
        Purchases.deleted_at.is_(None)  # 削除されていない購入のみ
    )).scalar()

def _get_post_and_creator_info(db: Session, post_id: str) -> tuple:
    """投稿とクリエイター情報を取得"""
    post = db.query(Posts).filter(
        Posts.id == post_id,
        Posts.deleted_at.is_(None)
    ).first()
    
    if not post:
        return None, None, None
    
    creator = db.query(Users).filter(Users.id == post.creator_user_id).first()
    creator_profile = db.query(Profiles).filter(Profiles.user_id == post.creator_user_id).first()
    
    return post, creator, creator_profile

def _get_post_categories(db: Session, post_id: str) -> list:
    """投稿のカテゴリ情報を取得"""
    return (
        db.query(Categories)
        .join(PostCategories, Categories.id == PostCategories.category_id)
        .filter(PostCategories.post_id == post_id)
        .filter(Categories.is_active == True)
        .all()
    )

def _get_likes_count(db: Session, post_id: str) -> int:
    """投稿のいいね数を取得"""
    return db.query(func.count(Likes.post_id)).filter(Likes.post_id == post_id).scalar() or 0

def _get_sale_info(db: Session, post_id: str) -> dict:
    """販売情報を取得・判定"""
    post_plans = (
        db.query(PostPlans, Plans, Prices)
        .join(Plans, PostPlans.plan_id == Plans.id)
        .join(Prices, Plans.id == Prices.plan_id)
        .filter(PostPlans.post_id == post_id)
        .filter(Plans.status == 1)
        .filter(Prices.status == 1)
        .all()
    )
    
    sale_type = "free"
    single = None
    subscription = None
    
    if post_plans:
        has_single = any(plan.type == PlanStatus.SINGLE for _, plan, _ in post_plans)
        has_subscription = any(plan.type == PlanStatus.PLAN for _, plan, _ in post_plans)
        
        if has_single and has_subscription:
            sale_type = "both"
        elif has_single:
            sale_type = "single"
        elif has_subscription:
            sale_type = "subscription"
        
        # 金額を取得
        for _, plan, price in post_plans:
            if plan.type == PlanStatus.SINGLE and single is None:
                single = {
                    "id": plan.id,
                    "amount": price.price,
                    "currency": price.currency
                }
            elif plan.type == PlanStatus.PLAN and subscription is None:
                subscription = {
                    "id": plan.id,
                    "amount": price.price,
                    "currency": price.currency,
                    "interval": price.interval,
                    "plan_name": plan.name,
                    "plan_description": plan.description,
                }
    
    return {
        "sale_type": sale_type,
        "single": single,
        "subscription": subscription
    }

def _get_media_info(db: Session, post_id: str, user_id: str | None) -> dict:
    """メディア情報を取得・処理"""
    media_assets = db.query(MediaAssets).filter(MediaAssets.post_id == post_id).all()
    purchased = _is_purchased(db, user_id, post_id) if user_id else False
    
    video_rendition = None
    thumbnail_key = None
    main_video_duration = None
    sample_video_duration = None
    
    for media_asset in media_assets:
        if media_asset.kind == MediaAssetKind.THUMBNAIL:
            thumbnail_key = media_asset.storage_key
        elif media_asset.kind in [MediaAssetKind.MAIN_VIDEO, MediaAssetKind.SAMPLE_VIDEO]:
            renditions = db.query(MediaRenditions).filter(
                MediaRenditions.asset_id == media_asset.id
            ).first()
            
            if renditions:
                # 購入状況に応じて適切な動画を設定
                if purchased and media_asset.kind == MediaAssetKind.MAIN_VIDEO:
                    video_rendition = renditions.storage_key
                elif not purchased and media_asset.kind == MediaAssetKind.SAMPLE_VIDEO:
                    video_rendition = renditions.storage_key
                
                # 動画の種類に応じてdurationを設定
                if media_asset.kind == MediaAssetKind.MAIN_VIDEO:
                    main_video_duration = get_video_duration(renditions.duration_sec)
                elif media_asset.kind == MediaAssetKind.SAMPLE_VIDEO:
                    sample_video_duration = get_video_duration(renditions.duration_sec)
    
    return {
        "video_rendition": video_rendition,
        "thumbnail_key": thumbnail_key,
        "main_video_duration": main_video_duration,
        "sample_video_duration": sample_video_duration,
        "purchased": purchased,
        "media_assets": media_assets
    }
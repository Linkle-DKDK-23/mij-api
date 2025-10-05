from fastapi import HTTPException
from sqlalchemy.orm import Session, aliased
from app.models.purchases import Purchases
from app.models.plans import Plans, PostPlans
from app.models.posts import Posts
from app.models.user import Users
from app.models.profiles import Profiles
from app.models.media_assets import MediaAssets
from app.constants.enums import PlanStatus, MediaAssetKind
from uuid import UUID
from typing import List
from app.models.prices import Prices
from app.schemas.purchases import SinglePurchaseResponse
import os

BASE_URL = os.getenv("CDN_BASE_URL")

def create_purchase(db: Session, purchase_data: dict):
    """
    購入情報を作成
    """
    purchase = Purchases(**purchase_data)
    db.add(purchase)
    db.flush()
    return purchase

def get_single_purchases_by_user_id(db: Session, user_id: UUID) -> List[SinglePurchaseResponse]:
    """
    ユーザーが単品購入した商品を取得（plan.type = 1）
    """
    # エイリアスを定義
    ThumbnailAssets = aliased(MediaAssets)

    results = (
        db.query(
            Purchases,
            Posts,
            Plans,
            Users.profile_name,
            Profiles.username,
            Profiles.avatar_url,
            ThumbnailAssets.storage_key.label('thumbnail_key'),
            Prices.price,
            Prices.currency
        )
        .join(Plans, Purchases.plan_id == Plans.id)
        .join(PostPlans, Plans.id == PostPlans.plan_id)  # PostPlansテーブルを介して結合
        .join(Posts, PostPlans.post_id == Posts.id)  # PostPlansからPostsへ結合
        .join(Users, Posts.creator_user_id == Users.id)
        .join(Profiles, Users.id == Profiles.user_id)
        .join(Prices, Plans.id == Prices.plan_id)
        .outerjoin(ThumbnailAssets, (Posts.id == ThumbnailAssets.post_id) & (ThumbnailAssets.kind == MediaAssetKind.THUMBNAIL))
        .filter(
            Purchases.user_id == user_id,
            Plans.type == PlanStatus.SINGLE,  # 単品のみ
            Plans.deleted_at.is_(None),
            Posts.deleted_at.is_(None)
        )
        .order_by(Purchases.created_at.desc())
        .all()
    )

    # レスポンス内容を整形する
    single_purchases = []
    for result in results:
        purchase, post, plan, profile_name, username, avatar_url, thumbnail_key, price, currency = result
        single_purchases.append(SinglePurchaseResponse(
            purchase_id=purchase.id,
            post_id=post.id,
            plan_id=plan.id,
            post_title=post.description[:50] if post.description else "",  # タイトルとして説明の最初の50文字を使用
            post_description=post.description,
            creator_name=profile_name,
            creator_username=username,
            creator_avatar_url= f"{BASE_URL}/{avatar_url}" if avatar_url else None,
            thumbnail_key= f"{BASE_URL}/{thumbnail_key}" if thumbnail_key else None,
            purchase_price=price or 0,
            purchase_created_at=purchase.created_at
        ))

    return single_purchases

def get_single_purchases_count_by_user_id(db: Session, user_id: UUID) -> int:
    """
    ユーザーが単品購入した商品数を取得
    """
    return (
        db.query(Purchases)
        .join(Plans, Purchases.plan_id == Plans.id)
        .filter(
            Purchases.user_id == user_id,
            Plans.type == PlanStatus.SINGLE,
            Plans.deleted_at.is_(None)
        )
        .count()
    )
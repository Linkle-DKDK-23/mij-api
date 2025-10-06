from fastapi import HTTPException
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, String
from app.models.purchases import Purchases
from app.models.plans import Plans, PostPlans
from app.models.posts import Posts
from app.models.user import Users
from app.models.profiles import Profiles
from app.models.media_assets import MediaAssets
from app.constants.enums import PlanStatus, MediaAssetKind
from uuid import UUID
from typing import List, Dict
from app.models.prices import Prices
from app.schemas.purchases import SinglePurchaseResponse
from datetime import datetime, date, timedelta
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
        .join(Posts, Purchases.post_id == Posts.id)  # 修正：Purchasesのpost_idを直接使用
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

def get_sales_data_by_creator_id(db: Session, creator_id: UUID, period: str = "today") -> Dict:
    """
    クリエイターの売上データを取得

    Args:
        db: データベースセッション
        creator_id: クリエイターのユーザーID
        period: 期間（"today", "monthly", "last_5_days"）

    Returns:
        Dict: 売上データ
    """
    # 期間に応じた日付フィルタを設定
    today = date.today()
    if period == "today":
        start_date = today
        end_date = today
    elif period == "monthly":
        # 当月の最初の日から今日まで
        start_date = today.replace(day=1)
        end_date = today
    elif period == "last_5_days":
        # 5日前から今日まで
        start_date = today - timedelta(days=4)
        end_date = today
    else:
        start_date = today
        end_date = today

    # 総売上を計算（自分の投稿に対する購入）
    total_sales_query = (
        db.query(func.sum(Prices.price))
        .select_from(Purchases)
        .join(Plans, Purchases.plan_id == Plans.id)
        .join(Prices, Plans.id == Prices.plan_id)
        .join(PostPlans, Plans.id == PostPlans.plan_id)
        .join(Posts, PostPlans.post_id == Posts.id)
        .filter(
            Posts.creator_user_id == creator_id,
            Purchases.deleted_at.is_(None),
            Plans.deleted_at.is_(None)
        )
    )
    total_sales = total_sales_query.scalar() or 0

    # 期間内の売上
    period_sales_query = (
        db.query(func.sum(Prices.price))
        .select_from(Purchases)
        .join(Plans, Purchases.plan_id == Plans.id)
        .join(Prices, Plans.id == Prices.plan_id)
        .join(PostPlans, Plans.id == PostPlans.plan_id)
        .join(Posts, PostPlans.post_id == Posts.id)
        .filter(
            Posts.creator_user_id == creator_id,
            func.date(Purchases.created_at) >= start_date,
            func.date(Purchases.created_at) <= end_date,
            Purchases.deleted_at.is_(None),
            Plans.deleted_at.is_(None)
        )
    )
    period_sales = period_sales_query.scalar() or 0

    # 期間内の単品売上
    single_item_sales_query = (
        db.query(func.sum(Prices.price))
        .select_from(Purchases)
        .join(Plans, Purchases.plan_id == Plans.id)
        .join(Prices, Plans.id == Prices.plan_id)
        .join(PostPlans, Plans.id == PostPlans.plan_id)
        .join(Posts, PostPlans.post_id == Posts.id)
        .filter(
            Posts.creator_user_id == creator_id,
            Plans.type == PlanStatus.SINGLE,
            func.date(Purchases.created_at) >= start_date,
            func.date(Purchases.created_at) <= end_date,
            Purchases.deleted_at.is_(None),
            Plans.deleted_at.is_(None)
        )
    )
    single_item_sales = single_item_sales_query.scalar() or 0

    # 期間内のプラン売上
    plan_sales_query = (
        db.query(func.sum(Prices.price))
        .select_from(Purchases)
        .join(Plans, Purchases.plan_id == Plans.id)
        .join(Prices, Plans.id == Prices.plan_id)
        .join(PostPlans, Plans.id == PostPlans.plan_id)
        .join(Posts, PostPlans.post_id == Posts.id)
        .filter(
            Posts.creator_user_id == creator_id,
            Plans.type == PlanStatus.PLAN,
            func.date(Purchases.created_at) >= start_date,
            func.date(Purchases.created_at) <= end_date,
            Purchases.deleted_at.is_(None),
            Plans.deleted_at.is_(None)
        )
    )
    plan_sales = plan_sales_query.scalar() or 0

    # 出金可能額（総売上の90%）
    withdrawable_amount = int(float(total_sales) * 0.9)

    return {
        "withdrawable_amount": withdrawable_amount,
        "total_sales": int(total_sales),
        "period_sales": int(period_sales),
        "single_item_sales": int(single_item_sales),
        "plan_sales": int(plan_sales)
    }

def get_sales_transactions_by_creator_id(db: Session, creator_id: UUID, limit: int = 50) -> List[Dict]:
    """
    クリエイターの売上履歴を取得

    Args:
        db: データベースセッション
        creator_id: クリエイターのユーザーID
        limit: 取得件数

    Returns:
        List[Dict]: 売上履歴
    """
    # 特定クリエイターのPlan IDを取得するサブクエリ
    creator_plans_subquery = (
        db.query(Plans.id.label('plan_id'))
        .select_from(Plans)
        .join(PostPlans, Plans.id == PostPlans.plan_id)
        .join(Posts, PostPlans.post_id == Posts.id)
        .filter(Posts.creator_user_id == creator_id)
        .distinct()
        .subquery()
    )

    # 各Planに対する最初のPostを取得するサブクエリ（文字列としてminを取得）
    post_subquery = (
        db.query(
            PostPlans.plan_id,
            func.min(func.cast(Posts.id, String)).label('first_post_id')
        )
        .join(Posts, PostPlans.post_id == Posts.id)
        .filter(Posts.creator_user_id == creator_id)
        .group_by(PostPlans.plan_id)
        .subquery()
    )

    transactions = (
        db.query(
            Purchases.id,
            Purchases.created_at,
            Plans.type,
            Plans.name.label('plan_name'),
            Posts.description.label('post_title'),
            Prices.price,
            Users.profile_name.label('buyer_name'),
            Profiles.username.label('buyer_username')
        )
        .select_from(Purchases)
        .join(Plans, Purchases.plan_id == Plans.id)
        .join(Prices, Plans.id == Prices.plan_id)
        .join(Users, Purchases.user_id == Users.id)
        .join(Profiles, Users.id == Profiles.user_id)
        .join(creator_plans_subquery, Plans.id == creator_plans_subquery.c.plan_id)
        .outerjoin(post_subquery, Plans.id == post_subquery.c.plan_id)
        .outerjoin(Posts, func.cast(Posts.id, String) == post_subquery.c.first_post_id)
        .filter(
            Purchases.deleted_at.is_(None),
            Plans.deleted_at.is_(None)
        )
        .order_by(Purchases.created_at.desc())
        .limit(limit)
        .all()
    )

    result = []
    for transaction in transactions:
        result.append({
            "id": str(transaction.id),
            "date": transaction.created_at.strftime('%Y/%m/%d'),
            "type": "single" if transaction.type == PlanStatus.SINGLE else "plan",
            "title": transaction.plan_name or (transaction.post_title[:50] if transaction.post_title else "無題"),
            "amount": int(transaction.price or 0),
            "buyer": transaction.buyer_name or transaction.buyer_username
        })

    return result
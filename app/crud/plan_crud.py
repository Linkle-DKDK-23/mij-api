from sqlalchemy.orm import Session
from app.models.plans import Plans
from app.models.subscriptions import Subscriptions
from app.models.prices import Prices
from uuid import UUID
from typing import List
from app.schemas.plan import PlanCreateRequest, PlanResponse, SubscribedPlanResponse
from app.constants.enums import PlanStatus
from datetime import datetime

def get_plan_by_user_id(db: Session, user_id: UUID) -> dict:
    """
    ユーザーが加入中のプラン数と詳細を取得
    """
    # 現在の日時を取得
    current_time = datetime.now()
    
    # 加入中のプランを取得
    subscribed_subscriptions = (
        db.query(Subscriptions)
        .join(Plans, Subscriptions.plan_id == Plans.id)
        .join(Prices, Plans.id == Prices.plan_id)
        .filter(
            Subscriptions.user_id == user_id,
            Subscriptions.status == 1,  # アクティブなサブスクリプション
            Subscriptions.canceled_at.is_(None),  # キャンセルされていない
            Subscriptions.current_period_end > current_time,  # 期間内
            Plans.type == PlanStatus.PLAN,  # プランタイプ
            Plans.deleted_at.is_(None)  # 削除されていないプラン
        )
        .all()
    )
    
    subscribed_plan_count = len(subscribed_subscriptions)
    subscribed_total_price = 0
    subscribed_plan_names = []
    subscribed_plan_details = []
    
    # 加入中のプランの詳細情報を取得
    for subscription in subscribed_subscriptions:
        price = db.query(Prices).filter(Prices.plan_id == subscription.plan_id).first()
        if price:
            subscribed_total_price += price.price
            subscribed_plan_names.append(subscription.plan.name)
            
            # 詳細情報を追加
            subscribed_plan_details.append({
                "subscription_id": subscription.id,
                "plan_id": subscription.plan.id,
                "plan_name": subscription.plan.name,
                "plan_description": subscription.plan.description,
                "price": price.price,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "subscription_created_at": subscription.created_at
            })
    
    return {
        "plan_count": subscribed_plan_count,
        "total_price": subscribed_total_price,
        "subscribed_plan_count": subscribed_plan_count,
        "subscribed_total_price": subscribed_total_price,
        "subscribed_plan_names": subscribed_plan_names,
        "subscribed_plan_details": subscribed_plan_details
    }

def create_plan(db: Session, plan_data) -> Plans:
    """
    プランを作成
    """
    db_plan = Plans(**plan_data)
    db.add(db_plan)
    db.flush()
    return db_plan

def get_user_plans(db: Session, user_id: UUID) -> List[PlanResponse]:
    """
    ユーザーのプラン一覧を取得
    """
    # priceテーブルと結合して金額情報を取得する
    plans = db.query(Plans).filter(
        Plans.creator_user_id == user_id,
        Plans.type == PlanStatus.PLAN,
        Plans.deleted_at.is_(None)
    ).join(Prices, Plans.id == Prices.plan_id).all()

    # レスポンス内容を整形する
    plans_response = []
    for plan in plans:
        # プランに関連する価格を取得（最初の価格を使用）
        price = db.query(Prices).filter(Prices.plan_id == plan.id).first()
        if price:
            plans_response.append(PlanResponse(
                id=plan.id,
                name=plan.name,
                description=plan.description,
                price=price.price
            ))

    return plans_response
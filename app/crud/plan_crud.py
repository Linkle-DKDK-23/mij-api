from sqlalchemy.orm import Session
from app.models.plans import Plans
from uuid import UUID
from typing import List
from app.schemas.plan import PlanCreateRequest
from app.models.prices import Prices
from app.schemas.plan import PlanResponse
from app.constants.enums import PlanStatus

def get_plan_counts(db: Session, user_id: UUID) -> dict:
    """
    ユーザーのプラン数と総額を取得
    """
    plans = db.query(Plans).filter(Plans.creator_user_id == user_id).filter(Plans.deleted_at.is_(None)).all()
    
    plan_count = len(plans)
    total_price = 0
    
    return {
        "plan_count": plan_count,
        "total_price": total_price
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

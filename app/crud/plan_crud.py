from sqlalchemy.orm import Session
from app.models.plans import Plans
from uuid import UUID
from typing import List
from app.schemas.plan import PlanCreateRequest

def get_plan_counts(db: Session, user_id: UUID) -> dict:
    """
    ユーザーのプラン数と総額を取得
    """
    plans = db.query(Plans).filter(Plans.creator_user_id == user_id).filter(Plans.deleted_at.is_(None)).all()
    
    plan_count = len(plans)
    total_price = sum(plan.price for plan in plans)
    
    return {
        "plan_count": plan_count,
        "total_price": total_price
    }

def create_plan(db: Session, user_id: UUID, plan_data: PlanCreateRequest) -> Plans:
    """
    プランを作成
    """
    db_plan = Plans(
        creator_user_id=user_id,
        name=plan_data.name,
        description=plan_data.description,
        price=plan_data.price,
        currency=plan_data.currency,
        billing_cycle=plan_data.billing_cycle,
        status=1
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def get_user_plans(db: Session, user_id: UUID) -> List[Plans]:
    """
    ユーザーのプラン一覧を取得
    """
    return db.query(Plans).filter(
        Plans.creator_user_id == user_id,
        Plans.deleted_at.is_(None)
    ).all()

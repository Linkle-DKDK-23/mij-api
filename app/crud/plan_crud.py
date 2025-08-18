from sqlalchemy.orm import Session
from app.models.plans import Plans
from uuid import UUID

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

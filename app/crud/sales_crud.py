from sqlalchemy.orm import Session
from app.models.payouts import CreatorBalances
from app.models.orders import OrderItems
from uuid import UUID
from sqlalchemy import func

def get_total_sales(db: Session, user_id: UUID) -> int:
    """
    ユーザーの総売上を取得
    """
    balance = db.query(CreatorBalances).filter(CreatorBalances.creator_user_id == user_id).first()
    if balance:
        return balance.available + balance.pending
    
    total_sales = (
        db.query(func.sum(OrderItems.amount))
        .filter(OrderItems.creator_user_id == user_id)
        .scalar()
    )
    
    return total_sales or 0

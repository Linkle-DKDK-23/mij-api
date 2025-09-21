from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.purchases import Purchases

def create_purchase(db: Session, purchase_data: dict):
    """
    購入情報を作成
    """
    purchase = Purchases(**purchase_data)
    db.add(purchase)
    db.flush()
    return purchase
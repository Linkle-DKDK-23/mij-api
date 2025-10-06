from sqlalchemy.orm import Session
from app.models.preregistrations import Preregistrations
from uuid import UUID
from typing import List

def is_preregistration_exists(db: Session, email: str) -> bool:
    """
    登録済みのアドレスかを確認する
    """
    return db.query(Preregistrations).filter(Preregistrations.email == email).first() is not None

def create_preregistration(db: Session, preregistration_data: Preregistrations) -> Preregistrations:
    """
    事前登録データを作成する
    Args:
        db: データベースセッション
        preregistration_data: 事前登録データ
    Returns:
        Preregistrations: 事前登録データ
    """
    db.add(preregistration_data)
    db.commit()
    db.refresh(preregistration_data)
    return preregistration_data

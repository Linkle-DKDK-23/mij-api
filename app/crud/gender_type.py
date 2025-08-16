from sqlalchemy.orm import Session
from app.models.creator_type import CreatorType
from typing import List
from app.models.gender import Gender


def create_creator_type(db: Session, creator_type: CreatorType) -> CreatorType:
    """
    クリエイタータイプを作成
    """
    db.add(creator_type)
    return creator_type
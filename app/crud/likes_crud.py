from sqlalchemy.orm import Session
from app.models.social import Likes
from uuid import UUID

def get_likes_count(db: Session, post_id: UUID) -> int:
    """
    いいね数を取得
    """
    likes_count = db.query(Likes).filter(Likes.post_id == post_id).count()
    return likes_count
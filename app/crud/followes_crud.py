from sqlalchemy.orm import Session
from app.models.social import Follows
from uuid import UUID

def get_follower_count(db: Session, user_id: UUID) -> dict:
    """
    フォロワー数を取得
    """
    followers_count = db.query(Follows).filter(Follows.creator_user_id == user_id).count()
    following_count = db.query(Follows).filter(Follows.follower_user_id == user_id).count()
    return {
        "followers_count": followers_count,
        "following_count": following_count
    }

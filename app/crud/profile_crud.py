from sqlalchemy.orm import Session
from app.models.profiles import Profiles
from uuid import UUID

def create_profile(db: Session, user_id: UUID, display_name: str) -> Profiles:
    """
    プロフィールを作成
    """
    db_profile = Profiles(
        user_id=user_id,
        display_name=display_name,
    )
    db.add(db_profile)
    db.flush()
    return db_profile

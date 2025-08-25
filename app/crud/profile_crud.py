from sqlalchemy.orm import Session
from app.models.profiles import Profiles
from uuid import UUID
from app.schemas.account import AccountUpdateRequest
from datetime import datetime

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


def get_profile_by_user_id(db: Session, user_id: UUID) -> Profiles:
    """
    ユーザーIDに紐づくプロフィールを取得
    """
    return db.query(Profiles).filter(Profiles.user_id == user_id).first()

def get_profile_by_display_name(db: Session, display_name: str) -> Profiles:
    """
    ディスプレイネームに紐づくプロフィールを取得
    """
    return db.query(Profiles).filter(Profiles.display_name == display_name).first()

def update_profile(db: Session, user_id: UUID, update_data: AccountUpdateRequest) -> Profiles:
    """
    プロフィールを更新
    """
    profile = get_profile_by_user_id(db, user_id)
    profile.display_name = update_data.display_name
    profile.bio = update_data.description
    profile.links = update_data.links
    profile.avatar_url = update_data.avatar_url
    profile.cover_url = update_data.cover_url
    profile.updated_at = datetime.now()
    db.add(profile)
    db.flush()
    return profile
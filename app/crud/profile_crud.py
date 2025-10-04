from sqlalchemy.orm import Session
from app.models.profiles import Profiles
from app.models.user import Users
from uuid import UUID
from app.schemas.account import AccountUpdateRequest
from datetime import datetime
from typing import Optional, Dict

def create_profile(db: Session, user_id: UUID, username: str) -> Profiles:
    """
    プロフィールを作成
    """
    db_profile = Profiles(
        user_id=user_id,
        username=username,
    )
    db.add(db_profile)
    db.flush()
    return db_profile

def exist_profile_by_username(db: Session, username: str) -> bool:
    """
    ユーザー名に紐づくプロフィールが存在するかを確認
    
    Args:
        db (Session): データベースセッション
        username (str): ユーザー名
        
    Returns:
        bool: プロフィールが存在する場合はTrue、存在しない場合はFalse
    """
    return db.query(Profiles).filter(Profiles.username == username).first() is not None

def get_profile_by_user_id(db: Session, user_id: UUID) -> Profiles:
    """
    ユーザーIDに紐づくプロフィールを取得
    """
    return db.query(Profiles).filter(Profiles.user_id == user_id).first()

def get_profile_by_username(db: Session, username: str) -> Profiles:
    """
    ユーザー名に紐づくプロフィールを取得
    """
    return db.query(Profiles).filter(Profiles.username == username).first()

def get_profile_info_by_user_id(db: Session, user_id: UUID) -> Dict[str, Optional[str]]:
    """
    ユーザーIDに紐づくプロフィール情報を取得（profile_name, username, avatar_url, cover_url）
    """
    result = (
        db.query(
            Users.profile_name,
            Profiles.username,
            Profiles.avatar_url,
            Profiles.cover_url
        )
        .join(Profiles, Users.id == Profiles.user_id)
        .filter(Users.id == user_id)
        .first()
    )
    
    if result:
        profile_name, username, avatar_url, cover_url = result
        return {
            "profile_name": profile_name,
            "username": username,
            "avatar_url": avatar_url if avatar_url else None,
            "cover_url": cover_url if cover_url else None
        }

def update_profile(db: Session, user_id: UUID, update_data: AccountUpdateRequest) -> Profiles:
    """
    プロフィールを更新
    """
    profile = get_profile_by_user_id(db, user_id)
    profile.username = update_data.username
    profile.bio = update_data.description
    profile.links = update_data.links
    profile.avatar_url = update_data.avatar_url
    profile.cover_url = update_data.cover_url
    profile.updated_at = datetime.now()
    db.add(profile)
    db.flush()
    return profile

def update_profile_by_x(db: Session, user_id: UUID, username: str):
    profile = db.query(Profiles).filter(Profiles.user_id == user_id).first()
    profile.username = username
    profile.updated_at = datetime.now()
    db.add(profile)
    db.flush()
    return profile
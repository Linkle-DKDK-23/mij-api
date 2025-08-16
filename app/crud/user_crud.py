from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import Users
from app.schemas.user import UserCreate
from app.core.security import hash_password
from sqlalchemy import select
from app.constants.enums import (
    AccountType, 
    AccountStatus
)

def create_user(db: Session, user_create: UserCreate) -> Users:
    """
    ユーザーを作成する

    Args:
        db: データベースセッション
        user_create: ユーザー作成情報
    """
    # ランダム文字列5文字作成
    db_user = Users(
        slug=user_create.name,
        email=user_create.email,
        password_hash=hash_password(user_create.password),
        role=AccountType.GENERAL_USER,
        status=AccountStatus.ACTIVE
    )
    db.add(db_user)
    db.flush()
    return db_user

def check_email_exists(db: Session, email: str) -> bool:
    """
    メールアドレスの重複チェック

    Args:
        db (Session): データベースセッション
        email (str): メールアドレス

    Returns:
        bool: 重複している場合はTrue、重複していない場合はFalse
    """
    result = db.query(Users).filter(Users.email == email).first()
    return result is not None

def check_slug_exists(db: Session, slug: str) -> bool:
    """
    スラッグの重複チェック

    Args:
        db (Session): データベースセッション
        slug (str): スラッグ

    Returns:
        bool: 重複している場合はTrue、重複していない場合はFalse
    """
    result = db.query(Users).filter(Users.slug == slug).first()
    return result is not None

def get_user_by_email(db: Session, email: str) -> Users:
    """
    メールアドレスによるユーザー取得

    Args:
        db (Session): データベースセッション
        email (str): メールアドレス

    Returns:
        Users: ユーザー情報
    """
    return db.scalar(select(Users).where(Users.email == email))

def get_user_by_id(db: Session, user_id: str) -> Users:
    """
    ユーザーIDによるユーザー取得

    Args:
        db (Session): データベースセッション
        user_id (str): ユーザーID

    Returns:
        Users: ユーザー情報
    """
    return db.get(Users, user_id)
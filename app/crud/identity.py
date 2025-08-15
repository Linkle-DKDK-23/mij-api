from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.identity import IdentityVerifications, IdentityDocuments
from app.constants.enums import IdentityKind
from datetime import datetime

def create_identity_verification(db: Session, user_id: str, status: int) -> IdentityVerifications:
    """
    認証情報作成

    Args:
        db (Session): データベースセッション
        user_id (str): ユーザーID
        status (int): ステータス

    Returns:
        IdentityVerifications: 認証情報
    """
    db_verification = IdentityVerifications(
        user_id=user_id,
        status=status,
        checked_at=None,
        notes=None
    )
    db.add(db_verification)
    db.commit()
    db.refresh(db_verification)
    return db_verification

def get_identity_verification_by_user_id(db: Session, user_id: str) -> IdentityVerifications:
    """
    ユーザーIDによる認証情報取得

    Args:
        db (Session): データベースセッション
        user_id (str): ユーザーID

    Returns:
        IdentityVerifications: 認証情報
    """
    return db.query(IdentityVerifications).filter(IdentityVerifications.user_id == user_id).first()


def create_identity_document(db: Session, verification_id: str, kind: int, storage_key: str) -> IdentityDocuments:
    """
    認証情報作成

    Args:
        db (Session): データベースセッション
        verification_id (str): 認証ID
        kind (int): 種類
        storage_key (str): ストレージキー

    Returns:
        IdentityDocuments: 認証情報
    """
    if kind == "front":
        kind = IdentityKind.FRONT
    elif kind == "back":
        kind = IdentityKind.BACK
    elif kind == "selfie":
        kind = IdentityKind.SELFIE

    db_document = IdentityDocuments(
        verification_id=verification_id,
        kind=kind,
        storage_key=storage_key
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def update_identity_verification(db: Session, verification_id: str, status: int, checked_at: datetime) -> IdentityVerifications:

    """
    認証情報更新

    Args:
        db (Session): データベースセッション
        verification_id (str): 認証ID
        status (int): ステータス
        checked_at (datetime): 確認日時

    Returns:
        IdentityVerifications: 認証情報
    """
    status = status
    db_verification = db.query(IdentityVerifications).filter(IdentityVerifications.id == verification_id).first()
    db_verification.status = status
    db_verification.checked_at = checked_at
    db.commit()
    db.refresh(db_verification)
    return db_verification
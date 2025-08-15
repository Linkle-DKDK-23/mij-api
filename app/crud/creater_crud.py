from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID
from datetime import datetime
from app.models.creators import Creators
from app.models.user import Users
from app.models.identity import IdentityVerifications, IdentityDocuments
from app.schemas.creator import CreatorCreate, CreatorUpdate, IdentityVerificationCreate, IdentityDocumentCreate
from app.constants.enums import CreatorStatus, VerificationStatus, AccountType

def create_creator(db: Session, creator_create: CreatorCreate, user_id: UUID) -> Creators:
    db_creator = Creators(
        user_id=user_id,
        name=creator_create.name,
        first_name_kana=creator_create.first_name_kana,
        last_name_kana=creator_create.last_name_kana,
        address=creator_create.address,
        phone_number=creator_create.phone_number,
        birth_date=creator_create.birth_date,
        status=CreatorStatus.ENTERED,
        tos_accepted_at=datetime.utcnow()
    )
    db.add(db_creator)

    # ユーザーのロール更新
    user = db.get(Users, user_id)
    if user:
        user.role = AccountType.CREATOR

    return db_creator

def update_creator_status(db: Session, user_id: UUID, status: CreatorStatus) -> Creators:
    """
    クリエイターステータスを更新する
    """
    creator = db.scalar(select(Creators).where(Creators.user_id == user_id))
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")
    
    creator.status = status
    return creator

def update_creator(db: Session, user_id: UUID, creator_update: CreatorUpdate) -> Creators:
    """
    クリエイター情報を更新する
    
    Args:
        db: データベースセッション
        user_id: ユーザーID
        creator_update: クリエイター更新情報
    """
    creator = db.scalar(select(Creators).where(Creators.user_id == user_id))
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")
    
    update_data = creator_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(creator, field, value)
    
    db.commit()
    db.refresh(creator)
    return creator

def get_creator_by_user_id(db: Session, user_id: UUID) -> Creators:
    """
    ユーザーIDによるクリエイター取得
    
    Args:
        db: データベースセッション
        user_id: ユーザーID
    """
    return db.scalar(select(Creators).where(Creators.user_id == user_id))

def create_identity_verification(db: Session, verification_create: IdentityVerificationCreate) -> IdentityVerifications:
    """
    本人確認レコードを作成する
    
    Args:
        db: データベースセッション
        verification_create: 本人確認作成情報
    """
    existing_verification = db.scalar(
        select(IdentityVerifications).where(IdentityVerifications.user_id == verification_create.user_id)
    )
    
    if existing_verification:
        return existing_verification
    
    db_verification = IdentityVerifications(
        user_id=verification_create.user_id,
        status=VerificationStatus.PENDING
    )
    db.add(db_verification)
    db.commit()
    db.refresh(db_verification)
    return db_verification

def update_identity_verification_status(db: Session, user_id: UUID, status: int, notes: str = None) -> IdentityVerifications:
    """
    本人確認ステータスを更新する
    
    Args:
        db: データベースセッション
        user_id: ユーザーID
        status: ステータス
        notes: 備考
    """
    verification = db.scalar(
        select(IdentityVerifications).where(IdentityVerifications.user_id == user_id)
    )
    
    if not verification:
        raise HTTPException(status_code=404, detail="Identity verification not found")
    
    verification.status = status
    verification.notes = notes
    if status == VerificationStatus.APPROVED:
        verification.checked_at = datetime.utcnow()
    
    db.commit()
    db.refresh(verification)
    return verification

def create_identity_document(db: Session, document_create: IdentityDocumentCreate) -> IdentityDocuments:
    """
    本人確認書類を作成する
    
    Args:
        db: データベースセッション
        document_create: 書類作成情報
    """
    db_document = IdentityDocuments(
        verification_id=document_create.verification_id,
        kind=document_create.kind,
        storage_key=document_create.storage_key
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def get_identity_verification_by_user_id(db: Session, user_id: UUID) -> IdentityVerifications:
    """
    ユーザーIDによる本人確認情報取得
    
    Args:
        db: データベースセッション
        user_id: ユーザーID
    """
    return db.scalar(
        select(IdentityVerifications).where(IdentityVerifications.user_id == user_id)
    )

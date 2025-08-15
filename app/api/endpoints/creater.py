from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.schemas.creator import (
    CreatorCreate, CreatorUpdate, CreatorOut,
    IdentityVerificationCreate, IdentityVerificationOut,
    IdentityDocumentCreate, IdentityDocumentOut
)
from app.db.base import get_db
from app.crud.creater_crud import (
    create_creator,
    update_creator,
    get_creator_by_user_id,
    create_identity_document,
    get_identity_verification_by_user_id
)
from app.deps.auth import get_current_user
from app.crud.gender_type import create_creator_type
from app.crud.gender import get_genders, get_gender_by_slug
from app.models.creator_type import CreatorType

router = APIRouter()

@router.post("/register", response_model=CreatorOut)
def register_creator(
    creator_create: CreatorCreate,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    クリエイター登録
    
    Args:
        creator_create (CreatorCreate): クリエイター登録情報
        user_id (UUID): ユーザーID
        db (Session): データベースセッション
    
    Returns:
        CreatorOut: クリエイター情報
    """
    try:
        existing_creator = get_creator_by_user_id(db, user.id)
        if existing_creator:
            raise HTTPException(status_code=400, detail="Creator already registered")
        

        creater = create_creator(db, creator_create, user.id)

        # 性別を取得
        genders = get_gender_by_slug(db, creator_create.gender_slug)
        insert_data = [
            {
                "user_id": user.id,
                "gender_id": gender_obj.id,
            }
            for gender_obj in genders
        ]
        db.bulk_insert_mappings(CreatorType, insert_data)

        # 変更をコミット
        db.commit()

        # コミット後にリフレッシュ
        db.refresh(creater)
        return creater
    except Exception as e:
        print("クリエイター登録エラー: ", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/profile", response_model=CreatorOut)
def update_creator_profile(
    creator_update: CreatorUpdate,
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """
    クリエイタープロフィール更新
    
    Args:
        creator_update (CreatorUpdate): クリエイター更新情報
        user_id (UUID): ユーザーID
        db (Session): データベースセッション
    
    Returns:
        CreatorOut: 更新されたクリエイター情報
    """
    try:
        return update_creator(db, user_id, creator_update)
    except Exception as e:
        print("クリエイタープロフィール更新エラー: ", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/verification-status", response_model=IdentityVerificationOut)
def get_verification_status(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """
    本人確認ステータス取得
    
    Args:
        user_id (UUID): ユーザーID
        db (Session): データベースセッション
    
    Returns:
        IdentityVerificationOut: 本人確認情報
    """
    try:
        verification = get_identity_verification_by_user_id(db, user_id)
        if not verification:
            raise HTTPException(status_code=404, detail="Identity verification not found")
        return verification
    except Exception as e:
        print("本人確認ステータス取得エラー: ", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile", response_model=CreatorOut)
def get_creator_profile(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """
    クリエイタープロフィール取得
    
    Args:
        user_id (UUID): ユーザーID
        db (Session): データベースセッション
    
    Returns:
        CreatorOut: クリエイター情報
    """
    try:
        creator = get_creator_by_user_id(db, user_id)
        if not creator:
            raise HTTPException(status_code=404, detail="Creator not found")
        return creator
    except Exception as e:
        print("クリエイタープロフィール取得エラー: ", e)
        raise HTTPException(status_code=500, detail=str(e))

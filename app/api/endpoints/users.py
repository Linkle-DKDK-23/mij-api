from fastapi import APIRouter, Depends, HTTPException, Query
from app.schemas.user import UserCreate, UserOut, UserProfileResponse
from app.db.base import get_db
from sqlalchemy.orm import Session
from app.crud.user_crud import (
    create_user,
    check_email_exists,
    check_slug_exists,
    get_user_profile_by_display_name
)
from app.api.commons.utils import generate_code
from app.deps.auth import get_current_user
from app.crud.profile_crud import create_profile
router = APIRouter()

@router.post("/register", response_model=UserOut)
def register_user(
    user_create: UserCreate, 
    db: Session = Depends(get_db)
):
    """
    ユーザー登録

    Args:
        user_create (UserCreate): ユーザー登録情報
        db (Session, optional): データベースセッション. Defaults to Depends(get_db).

    Raises:
        HTTPException: メールアドレスが既に登録されている場合

    Returns:
        UserOut: ユーザー情報
    """
    try:
        is_email_exists = check_email_exists(db, user_create.email)
        if is_email_exists:
            raise HTTPException(status_code=400, detail="存在しているメールアドレスです")
        is_slug_exists = check_slug_exists(db, user_create.name)
        if is_slug_exists:
            raise HTTPException(status_code=400, detail="存在しているユーザー名です")
        
        for _ in range(10):  # 最大10回リトライ
            slug_code = generate_code(5)
            is_slug_exists = check_slug_exists(db, slug_code)
            if not is_slug_exists:
                break
            raise HTTPException(status_code=500, detail="ユーザー名の生成に失敗しました")

        db_user = create_user(db, user_create)
        db_profile = create_profile(db, db_user.id, slug_code)

        db.commit()
        db.refresh(db_user)
        db.refresh(db_profile)

        return db_user
    except Exception as e:
        print("ユーザー登録エラー: ", e)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profile", response_model=UserProfileResponse)
def get_user_profile_by_slug_endpoint(
    display_name: str = Query(..., description="ユーザー名"),
    db: Session = Depends(get_db)
):
    """
    ディスプレイネームによるユーザープロフィール取得
    """
    try:
        profile_data = get_user_profile_by_display_name(db, display_name)
        if not profile_data:
            raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
        
        user = profile_data["user"]
        profile = profile_data["profile"]
        
        website_url = None
        if profile and profile.links and isinstance(profile.links, dict):
            website_url = profile.links.get("website")
        
        return UserProfileResponse(
            id=user.id,
            slug=user.slug,
            display_name=profile.display_name if profile else None,
            avatar_url=profile.avatar_url if profile else None,
            cover_url=profile.cover_url if profile else None,
            bio=profile.bio if profile else None,
            website_url=website_url,
            post_count=len(profile_data["posts"]),
            follower_count=0,
            posts=profile_data["posts"],
            plans=profile_data["plans"],
            individual_purchases=profile_data["individual_purchases"],
            gacha_items=profile_data["gacha_items"]
        )
    except Exception as e:
        print("ユーザープロフィール取得エラー: ", e)
        raise HTTPException(status_code=500, detail=str(e))
    
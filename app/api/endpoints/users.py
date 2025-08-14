from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import UserCreate, UserOut
from app.db.base import get_db
from sqlalchemy.orm import Session
from app.crud.user_crud import (
    create_user,
    check_email_exists,
    check_slug_exists
)

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
            raise HTTPException(status_code=400, detail="Email already registered")
        is_slug_exists = check_slug_exists(db, user_create.name)
        if is_slug_exists:
            raise HTTPException(status_code=400, detail="Slug already registered")

        return create_user(db, user_create)
    except Exception as e:
        print("ユーザー登録エラー: ", e)
        raise HTTPException(status_code=500, detail=str(e))
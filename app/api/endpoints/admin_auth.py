from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.core.security import verify_password, create_access_token
from app.crud.user_crud import get_user_by_email
from app.schemas.admin import AdminLoginRequest, AdminLoginResponse, AdminUserResponse
from app.deps.auth import get_current_admin_user
from app.models.user import Users
from app.constants.enums import AccountType

router = APIRouter()
security = HTTPBearer()

@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(
    credentials: AdminLoginRequest,
    db: Session = Depends(get_db)
):
    """管理者ログイン"""
    
    # ユーザー取得
    user = get_user_by_email(db, email=credentials.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # パスワード確認
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # 管理者権限確認 (roleは数値: 1=user, 2=creator, 3=admin)
    if user.role != AccountType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # JWTトークン生成
    access_token = create_access_token(sub=str(user.id))
    
    return AdminLoginResponse(
        token=access_token,
        user=AdminUserResponse.from_orm(user)
    )

@router.post("/logout")
async def admin_logout(
    current_admin: Users = Depends(get_current_admin_user)
):
    """管理者ログアウト"""
    # JWTトークンはステートレスなので、フロントエンド側でトークンを削除するだけ
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=AdminUserResponse)
async def get_current_admin(
    current_admin: Users = Depends(get_current_admin_user)
):
    """現在の管理者情報を取得"""
    return AdminUserResponse.from_orm(current_admin)
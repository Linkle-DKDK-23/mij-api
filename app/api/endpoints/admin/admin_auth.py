from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.base import get_db
from app.core.security import verify_password, create_access_token, create_refresh_token, new_csrf_token
from app.core.cookies import set_auth_cookies
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
    response: Response,
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

    # ログイン時刻を更新
    user.last_login_at = datetime.utcnow()
    db.commit()

    # JWTトークン生成
    access_token = create_access_token(sub=str(user.id))
    refresh_token = create_refresh_token(sub=str(user.id))
    csrf_token = new_csrf_token()

    # Cookieに認証情報を設定
    set_auth_cookies(response, access_token, refresh_token, csrf_token)

    return AdminLoginResponse(
        token=access_token,
        user=AdminUserResponse.from_orm(user)
    )

@router.post("/logout")
async def admin_logout(
    response: Response,
    current_admin: Users = Depends(get_current_admin_user)
):
    """管理者ログアウト"""
    from app.core.cookies import clear_auth_cookies

    # Cookieから認証情報をクリア
    clear_auth_cookies(response)
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=AdminUserResponse)
async def get_current_admin(
    current_admin: Users = Depends(get_current_admin_user)
):
    """現在の管理者情報を取得"""
    return AdminUserResponse.from_orm(current_admin)
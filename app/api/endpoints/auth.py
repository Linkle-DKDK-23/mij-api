from fastapi import APIRouter, Depends, HTTPException, status, Header, Response
from app.core.security import create_access_token, decode_token
from app.db.base import get_db
from app.schemas.auth import LoginIn, TokenOut, LoginCookieOut
from app.models.user import Users
from sqlalchemy.orm import Session
from app.core.security import verify_password
from app.crud.user_crud import get_user_by_email, get_user_by_id
from app.core.security import (
    verify_password, 
    create_access_token, 
    create_refresh_token, 
    decode_token, 
    new_csrf_token
)
from app.core.cookies import set_auth_cookies, clear_auth_cookies, REFRESH_COOKIE, CSRF_COOKIE
from app.deps.auth import get_current_user


router = APIRouter()

@router.post("/login", response_model=LoginCookieOut)
def login(payload: LoginIn, response: Response, db: Session = Depends(get_db)):
    """
    ログイン

    Args:
        payload (LoginIn): ログイン情報
        db (Session, optional): データベースセッション. Defaults to Depends(get_db).

    Raises:
        HTTPException: ユーザーが存在しない場合
        HTTPException: ユーザーが非アクティブの場合

    Returns:
        TokenOut: トークン
    """
    try:
        email = payload.email
        password = payload.password
        user = get_user_by_email(db, email)
        if not user or not verify_password(password, user.password_hash):

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if getattr(user, "is_active", True) is False:
            raise HTTPException(status_code=403, detail="User is not active")
        
        
        access = create_access_token(str(user.id))
        refresh = create_refresh_token(str(user.id))
        csrf = new_csrf_token()

        set_auth_cookies(response, access, refresh, csrf)
        return {
            "message": "logged in", 
            "csrf_token": csrf
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 認可テスト用の /auth/me
@router.get("/me")
def me(user: Users = Depends(get_current_user)):
    """
    ユーザー情報取得

    Args:
        user (Users): ユーザー

    Returns:
        dict: ユーザー情報
    """
    try:
        return {"id": str(user.id), "email": user.email}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logout")
def logout(response: Response):
    """
    ログアウト

    Args:
        response (Response): レスポンス
    """
    try:
        clear_auth_cookies(response)
        return {"message": "logged out"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/refresh")
def refresh_token(response: Response, refresh_token: str | None = Header(default=None),  # 使わない例
                  csrf_token: str | None = Header(default=None),  # 使わない例
                  # 実際は Cookie から読む:
                  refresh_cookie: str | None = Depends(lambda refresh_token=Header(None): None),
                  # 上の書き方は型合わせのダミー。実際は Request.cookies を読むか、以下のように直接引数で:
                  ):
    # Request から Cookie を読む実装の方が分かりやすい
    # → ここでは簡単のため、後段の get_refresh_from_cookie を使う
    test = "aaaa"
    raise HTTPException(status_code=500, detail="Use the version below")  # ダミー
from fastapi import APIRouter, Depends, HTTPException, status, Header, Response, Request
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
from app.core.cookies import set_auth_cookies, clear_auth_cookies, REFRESH_COOKIE, CSRF_COOKIE, ACCESS_COOKIE
from app.core.config import settings
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
def refresh_token(request: Request, response: Response):
    refresh = request.cookies.get(REFRESH_COOKIE)
    if not refresh:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")

    try:
        payload = decode_token(refresh)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    user_id = payload.get("sub")
    # 必要ならDBでBAN/退会チェックなど

    # 新しい短命Access & CSRF
    new_access = create_access_token(user_id)
    new_csrf = new_csrf_token()

    # Set-Cookie（Access: HttpOnly / CSRF: 非HttpOnly）
    response.set_cookie(
        ACCESS_COOKIE, new_access,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MIN * 60,
        domain=settings.COOKIE_DOMAIN, secure=settings.COOKIE_SECURE,
        httponly=True, samesite=settings.COOKIE_SAMESITE, path=settings.COOKIE_PATH,
    )
    response.set_cookie(
        CSRF_COOKIE, new_csrf,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MIN * 60,
        domain=settings.COOKIE_DOMAIN, secure=settings.COOKIE_SECURE,
        httponly=False, samesite=settings.COOKIE_SAMESITE, path=settings.COOKIE_PATH,
    )
    return {"message": "refreshed", "csrf_token": new_csrf}


@router.get("/csrf")
def get_csrf_token(request: Request):
    csrf = request.cookies.get(CSRF_COOKIE)

    print(f"csrf_header={request.headers.get('csrf-token') or request.headers.get('x-csrf-token')}")
    print(f"cookies={request.cookies}")
    print(f"csrf={csrf}")
    if not csrf:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing CSRF token")
    
    return "ok"


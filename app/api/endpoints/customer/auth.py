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
from datetime import datetime, timedelta
import os, httpx

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
        
        # ログイン時刻を更新
        user.last_login_at = datetime.utcnow()
        db.commit()
        
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
def me(user: Users = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    ユーザー情報取得

    Args:
        user (Users): ユーザー
        db (Session): データベースセッション

    Returns:
        dict: ユーザー情報
    """
    try:
        # 48時間（2日）チェック
        if user.last_login_at:
            time_since_last_login = datetime.utcnow() - user.last_login_at
            if time_since_last_login > timedelta(hours=48):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="Session expired due to inactivity"
                )
        
        # アクセス時刻を更新
        user.last_login_at = datetime.utcnow()
        db.commit()
        
        return {"id": str(user.id), "email": user.email, "role": user.role}
    except HTTPException:
        raise
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


@router.get("/auth/callback")
async def auth_callback(code: str):
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(
            f"{os.getenv('COGNITO_DOMAIN')}/oauth2/token",
            data={
                "grant_type": "authorization_code",
                "client_id": os.getenv('CLIENT_ID'),
                "code": code,
                "redirect_uri": os.getenv('REDIRECT_URI'),
                # "code_verifier": "<フロントで保持したverifier>"  # PKCE時に必要
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    if r.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Token exchange failed: {r.text}")

    tokens = r.json()

    # Cookieに保存 (本番は secure=True, samesite="None")
    res = Response(status_code=302, headers={"Location": "/"})
    res.set_cookie("cognito_id_token", tokens["id_token"], httponly=True, samesite="Lax", secure=False)
    res.set_cookie("cognito_access_token", tokens["access_token"], httponly=True, samesite="Lax", secure=False)
    if "refresh_token" in tokens:
        res.set_cookie("cognito_refresh_token", tokens["refresh_token"], httponly=True, samesite="Lax", secure=False)

    return res

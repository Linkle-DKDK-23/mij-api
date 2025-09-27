# app/deps/auth.py
from fastapi import Depends, HTTPException, status, Cookie, Header
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.core.security import decode_token
from app.core.cookies import ACCESS_COOKIE
from app.models.user import Users
from app.crud.user_crud import get_user_by_id


def get_current_user(
    db: Session = Depends(get_db),
    access_token: str | None = Cookie(default=None, alias=ACCESS_COOKIE),
):
    if not access_token:
        raise HTTPException(status_code=401, detail="Missing access token")
    try:
        payload = decode_token(access_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")
    user_id = payload.get("sub")
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_current_user_optional(
    db: Session = Depends(get_db),
    access_token: str | None = Cookie(default=None, alias=ACCESS_COOKIE),
):
    """オプショナル認証 - トークンがない場合はNoneを返す"""
    if not access_token:
        return None
    try:
        payload = decode_token(access_token)
        if payload.get("type") != "access":
            return None
        user_id = payload.get("sub")
        user = get_user_by_id(db, user_id)
        return user
    except Exception:
        return None


def get_current_admin_user(
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """管理者用認証 - Bearerトークンを使用"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.split(" ")[1]
    
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    user = get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 管理者権限確認 (roleは数値: 1=user, 2=creator, 3=admin)
    if user.role != 3:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return user

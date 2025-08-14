# app/deps/auth.py
from fastapi import Depends, HTTPException, status, Cookie
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

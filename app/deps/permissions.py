# app/deps/permissions_min.py
from fastapi import Depends, HTTPException, status
from app.deps.auth import get_current_user  # 既存のCookie→User解決
from app.models.user import Users

def _has_role(user: Users, role: str) -> bool:
    r = getattr(user, "role", None)
    return r == "admin" or r == role

def require_creator_auth(user: Users = Depends(get_current_user)) -> Users:
    if not _has_role(user, "creator"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="creator role required")
    return user

def require_kyc_reviewer(user: Users = Depends(get_current_user)) -> Users:
    if not _has_role(user, "kyc_reviewer"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="kyc_reviewer role required")
    return user

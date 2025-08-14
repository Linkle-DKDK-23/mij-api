# app/core/cookies.py
from fastapi import Response
from app.core.config import settings

ACCESS_COOKIE = "access_token"
REFRESH_COOKIE = "refresh_token"
CSRF_COOKIE = "csrf_token"

def set_auth_cookies(response: Response, access_token: str, refresh_token: str, csrf_token: str):
    common = {
        "domain": settings.COOKIE_DOMAIN,
        "secure": settings.COOKIE_SECURE,
        "httponly": True,
        "samesite": settings.COOKIE_SAMESITE,
        "path": settings.COOKIE_PATH,
    }
    # Access: 短命
    response.set_cookie(
        ACCESS_COOKIE, access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MIN * 60, **common
    )
    # Refresh: 長命
    response.set_cookie(
        REFRESH_COOKIE, refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60, **common
    )
    # CSRF: JS から読める（HttpOnly=False）
    response.set_cookie(
        CSRF_COOKIE, csrf_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MIN * 60,
        domain=settings.COOKIE_DOMAIN,
        secure=settings.COOKIE_SECURE,
        httponly=False,  # ← ここがポイント（Double Submit 用）
        samesite=settings.COOKIE_SAMESITE,
        path=settings.COOKIE_PATH,
    )

def clear_auth_cookies(response: Response):
    for name in (ACCESS_COOKIE, REFRESH_COOKIE, CSRF_COOKIE):
        response.delete_cookie(
            name, domain=settings.COOKIE_DOMAIN, path=settings.COOKIE_PATH
        )

# app/middlewares/csrf.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.core.cookies import CSRF_COOKIE

EXCLUDE_PATHS = {"/auth/login", "/auth/refresh", "/auth/logout"}  # 認証系はここで免除

class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
            return await call_next(request)
        if request.url.path in EXCLUDE_PATHS:
            return await call_next(request)

        header_token = request.headers.get("X-CSRF-Token")
        cookie_token = request.cookies.get(CSRF_COOKIE)

        if not header_token or not cookie_token or header_token != cookie_token:
            return JSONResponse({"detail": "CSRF token mismatch"}, status_code=403)

        return await call_next(request)

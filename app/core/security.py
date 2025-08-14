# app/core/security.py
from passlib.context import CryptContext
import jwt
from app.core.config import settings
import datetime as dt
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 12

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain: str) -> str:
    """
    パスワードをハッシュ化する

    Args:
        plain: 平文のパスワード
    """
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    """
    パスワードを検証する

    Args:
        plain: 平文のパスワード
        hashed: ハッシュ化されたパスワード
    """
    return pwd_context.verify(plain, hashed)

def now_utc() -> dt.datetime:
    """
    現在のUTC時刻を取得する
    """
    return dt.datetime.utcnow()

def create_access_token(sub: str) -> str:
    """
    アクセストークンを作成する

    Args:
        sub (str): ユーザーID

    Returns:
        str: アクセストークン
    """
    iat = now_utc()
    exp = iat + dt.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MIN)
    payload = {"sub": sub, "iat": iat, "exp": exp, "type": "access"}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(sub: str) -> str:
    """
    リフレッシュトークンを作成する

    Args:
        sub (str): ユーザーID

    Returns:
        str: リフレッシュトークン
    """
    iat = now_utc()
    exp = iat + dt.timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": sub, "iat": iat, "exp": exp, "type": "refresh"}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    """
    トークンをデコードする

    Args:
        token (str): トークン

    Returns:
        dict: デコードされたトークン
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])


def new_csrf_token() -> str:
    """
    新しいCSRFトークンを生成する

    Returns:
        str: 新しいCSRFトークン
    """
    return secrets.token_urlsafe(16)
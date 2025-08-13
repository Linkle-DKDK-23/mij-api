# app/core/security.py
from passlib.context import CryptContext
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

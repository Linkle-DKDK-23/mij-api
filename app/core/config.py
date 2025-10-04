# app/core/config.py
import os
from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # データベース設定
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    # トークン設定
    ACCESS_TOKEN_EXPIRE_MIN: int = 43200
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14
    COOKIE_DOMAIN: str | None = None
    COOKIE_SECURE: bool = True
    COOKIE_SAMESITE: str = "lax"
    COOKIE_PATH: str = "/"

    # メール設定
    EMAIL_ENABLED: bool = True
    EMAIL_BACKEND: str = "mailhog"  # mailhog | ses
    MAIL_FROM: EmailStr = "no-reply@example.com"
    MAILHOG_HOST: str = "127.0.0.1"
    MAILHOG_PORT: int = 1025
    AWS_REGION: str = "ap-northeast-1"
    SES_CONFIGURATION_SET: str | None = None

    model_config = SettingsConfigDict(
        env_file=[".env.development", ".env", ".env.local"],
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

settings = Settings()

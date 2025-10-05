from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from app.db.base import get_db
from sqlalchemy.orm import Session
from app.crud.email_verification_crud import (
    issue_verification_token, 
    remake_email_verification_token, 
    get_verification_token,
    update_verification_token
)
from app.crud.user_crud import update_user_email_verified_at
from app.services.email.send_email import send_email_verification
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.user import Users
import hashlib
from datetime import datetime, timezone
from app.core.config import settings
from app.schemas.user import UserCreate
from app.crud.user_crud import resend_email_verification
import os
from app.schemas.auth_email_verify import VerifyIn
router = APIRouter()


@router.post("/verify")
def verify(body: VerifyIn, db: AsyncSession = Depends(get_db)):
    """メールアドレスの認証

    Args:
        body (VerifyIn): 認証情報
        db (AsyncSession, optional): データベースセッション. Defaults to Depends(get_db).

    Raises:
        HTTPException: リンクが無効か、期限切れです。
        HTTPException: メールアドレスの認証に失敗しました

    Returns:
        dict: メールアドレスの認証結果
    """
    try:
        token_hash = hashlib.sha256(body.token.encode()).hexdigest()
        rec = get_verification_token(db, token_hash)
        if not rec or rec.consumed_at is not None or rec.expires_at < datetime.utcnow():
            raise HTTPException(status_code=400, detail="リンクが無効か、期限切れです。")

        # 成功: ユーザーを検証済みに
        update_user_email_verified_at(db, rec.user_id)
        # トークン全無効化
        update_verification_token(db, rec.user_id)
        db.commit()
        return {"result": True}
    except Exception as e:
        db.rollback()
        print("メールアドレスの認証エラーが発生しました", e)
        raise HTTPException(500, f"Failed to verify: {e}")

@router.post("/resend")
def verify_email(
    user_create: UserCreate, 
    db: Session = Depends(get_db), 
    background: BackgroundTasks = BackgroundTasks()
):
    """
    メールアドレスの再送信

    Args:
        user_create (UserCreate): ユーザー登録情報
        db (Session, optional): データベースセッション
        background (BackgroundTasks, optional): バックグラウンドタスク

    Returns:
        dict: メールアドレスの再送信結果

    Raises:
        HTTPException: メールアドレスの再送信に失敗した場合
    """
    try:
        user = resend_email_verification(db, user_create.email)

        if user and not user.is_email_verified:
            raw = remake_email_verification_token(db, user.id)

            verify_url = f"{os.getenv('FRONTEND_URL')}/auth/verify-email?token={raw}"
            background.add_task(send_email_verification, user.email, verify_url, user.display_name if hasattr(user, "display_name") else None)
            db.commit()
            db.refresh(user)
        return {"message": "email resend"}
    except Exception as e:
        print("メールアドレスの再送信エラーが発生しました", e)
        raise HTTPException(500, f"Failed to resend: {e}")
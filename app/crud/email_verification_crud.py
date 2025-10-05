# app/services/email_verification.py
import base64, os, hashlib, uuid
from datetime import datetime, timedelta, timezone
from pydantic import EmailStr
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models import EmailVerificationTokens
from fastapi import BackgroundTasks
import os
from app.api.commons.utils import generate_email_verification_token

def issue_verification_token(db: AsyncSession, user_id: uuid.UUID, ttl_hours=24, rotate=True):
    """メールアドレスの認証トークンを発行

    Args:
        db (AsyncSession): データベースセッション
        user_id (uuid.UUID): ユーザーID
        ttl_hours (int, optional): _description_. Defaults to 24.
        rotate (bool, optional): トークンを再発行するかどうか. Defaults to True.

    Returns:
        str: メールアドレスの認証トークン
        datetime: トークンの有効期限
    """
    # 既存トークン無効化（任意: rotate True の場合）
    if rotate:
        result = db.execute(
            update(EmailVerificationTokens)
            .where(EmailVerificationTokens.user_id==user_id, EmailVerificationTokens.consumed_at.is_(None))
            .values(consumed_at=datetime.utcnow())
        )
    raw, token_hash = generate_email_verification_token()
    expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
    rec = EmailVerificationTokens(id=uuid.uuid4(), user_id=user_id, token_hash=token_hash, expires_at=expires_at)
    db.add(rec)
    db.commit()
    return raw, expires_at


def get_verification_token(db: AsyncSession, token_hash: str):
    """メールアドレスの認証トークンを取得
    """
    stmt = select(EmailVerificationTokens).where(EmailVerificationTokens.token_hash==token_hash)
    result = db.execute(stmt)
    rec = result.scalar_one_or_none()
    return rec

def update_verification_token(db: AsyncSession, user_id: uuid.UUID):
    """メールアドレスの認証トークンを更新
    """
    db.execute(
        update(EmailVerificationTokens)
        .where(EmailVerificationTokens.user_id==user_id, EmailVerificationTokens.consumed_at.is_(None))
        .values(consumed_at=datetime.utcnow())
    )

async def remake_email_verification_token(db: AsyncSession, user_id: uuid.UUID):
    """メールアドレスの再送信

    Args:
        db (AsyncSession): データベースセッション
        user_id (uuid.UUID): ユーザーID

    Raises:
        HTTPException: メールアドレスの再送信に失敗した場合

    Returns:
        str: メールアドレスの再送信結果（トークン）
    """
    cooldown = 60
    result = await db.execute(
        select(EmailVerificationTokens).where(EmailVerificationTokens.user_id==user_id, EmailVerificationTokens.consumed_at.is_(None)
    ).order_by(EmailVerificationTokens.last_sent_at.desc()))
    t = result.scalars().first()
    if t and (datetime.utcnow() - t.last_sent_at).total_seconds() < cooldown:
        raise HTTPException(status_code=429, detail="少し待ってから再度お試しください。")

    raw, _ = await issue_verification_token(db, user_id, ttl_hours=24)
    await db.execute(
        update(EmailVerificationTokens)
        .where(EmailVerificationTokens.token_hash == hashlib.sha256(raw.encode()).hexdigest())
        .values(sent_count=(t.sent_count+1 if t else 1), last_sent_at=datetime.utcnow())
    )

    return raw
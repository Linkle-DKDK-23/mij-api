import uuid
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict
from app.schemas.identity import (
    PresignResponse, 
    PresignRequest, 
    UploadItem, 
    Kind, 
    CompleteRequest, 
    PresignResponseItem, 
    VerifyRequest, 
)
from app.deps.permissions import require_creator_auth
from app.services.s3.keygen import identity_key
from app.services.s3.presign import presign_put
from app.deps.auth import get_current_user
from app.constants.enums import IdentityStatus, IdentityKind
from app.crud.identity import create_identity_verification, create_identity_document, update_identity_verification
from app.db.base import get_db
from sqlalchemy.orm import Session
from datetime import datetime, timezone

router = APIRouter()

from app.services.s3.client import s3_client, IDENTITY_BUCKET, KMS_ALIAS_IDENTITY
s3 = s3_client()

@router.post("/")
async def kyc_upload():
    return {"message": "KYC upload"}



@router.post("/presign-upload")
def kyc_presign_upload(
    body: PresignRequest, 
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    """
    Presign upload

    Raises:
        HTTPException: 

    Returns:
        _type_: 
    """

    try:
        allowed_kinds = {"front","back","selfie"}

        seen = set()
        for f in body.files:
            if f.kind not in allowed_kinds:
                raise HTTPException(400, f"unsupported kind: {f.kind}")
            if f.kind in seen:
                raise HTTPException(400, f"duplicated kind: {f.kind}")
            seen.add(f.kind)
        uploads: Dict[Kind, UploadItem] = {}
        
        verification = create_identity_verification(db,  str(user.id), IdentityStatus.PENDING)

        for f in body.files:
            key = identity_key(str(user.id), verification.id, f.kind, f.ext)
            try:
                url = s3.generate_presigned_url(
                    "put_object",
                    Params={
                        "Bucket": IDENTITY_BUCKET,
                        "Key": key,
                        "ContentType": f.content_type,
                        "ServerSideEncryption": "aws:kms",
                        "SSEKMSKeyId": KMS_ALIAS_IDENTITY,
                    },
                    ExpiresIn=300,
                )
            except Exception:
                raise HTTPException(500, "Failed to issue presigned URL")
            
            uploads[f.kind] = PresignResponseItem(
                key=key,
                upload_url=url,
                expires_in=300,
                required_headers = {
                    "Content-Type": f.content_type,
                    "x-amz-server-side-encryption": "aws:kms",
                    "x-amz-server-side-encryption-aws-kms-key-id": KMS_ALIAS_IDENTITY,
                }
            )
            
            create_identity_document(db, verification.id, f.kind, key)

        return PresignResponse(verification_id=verification.id, uploads=uploads)
    except Exception as e:
        print("認証情報作成エラーが発生しました", e)
        raise HTTPException(500, f"Failed to issue presigned URL: {e}")


@router.post("/complete")
def kyc_complete(
    body: VerifyRequest, 
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    try:
        required = {"front","back","selfie"}
        present = {f.kind for f in body.files}
        missing = required - present
        extra   = present - required
        if missing:
            raise HTTPException(400, f"missing kinds: {sorted(missing)}")
        if extra:
            raise HTTPException(400, f"unsupported kinds: {sorted(extra)}")

        # S3存在確認
        for f in body.files:
            key = identity_key(str(user.id), str(body.verification_id), f.kind, f.ext)
            try:
                s3.head_object(Bucket=IDENTITY_BUCKET, Key=key)
            except Exception:
                raise HTTPException(400, f"missing uploaded file: {f.kind}")

        update_identity_verification(
            db, body.verification_id, IdentityStatus.APPROVED, datetime.now(timezone.utc)
        )
        return {"ok": True, "verification_id": str(body.verification_id)}
    except Exception as e:
        print("認証情報更新エラーが発生しました", e)
        raise HTTPException(500, f"Failed to complete: {e}")

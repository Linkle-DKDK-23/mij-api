# app/services/s3/presign.py
from typing import Literal, Optional
from .client import s3_client, VIDEO_BUCKET, IDENTITY_BUCKET, KMS_ALIAS_VIDEO, KMS_ALIAS_IDENTITY

Resource = Literal["video", "identity"]

def _bucket_and_kms(resource: Resource):
    if resource == "video":
        return VIDEO_BUCKET, KMS_ALIAS_VIDEO
    elif resource == "identity":
        return IDENTITY_BUCKET, KMS_ALIAS_IDENTITY
    raise ValueError("unknown resource")

def presign_put(
    resource: Resource,
    key: str,
    content_type: str,
    expires_in: int = 300
) -> dict:
    """
    Presign upload

    Args:
        resource (Resource): リソース
        key (str): キー
        content_type (str): コンテントタイプ
        expires_in (int): 有効期限

    Returns:
        dict: プレシグネットURL
    """
    bucket, kms_alias = _bucket_and_kms(resource)
    client = s3_client()
    params = {
        "Bucket": bucket,
        "Key": key,
        "ContentType": content_type,
        "ServerSideEncryption": "aws:kms",
        "SSEKMSKeyId": kms_alias,
    }
    url = client.generate_presigned_url(
        "put_object",
        Params=params,
        ExpiresIn=expires_in,
    )
    return {
        "upload_url": url,
        "key": key,
        "expires_in": expires_in,
        "required_headers": {
            "Content-Type": content_type,
            "x-amz-server-side-encryption": "aws:kms",
            "x-amz-server-side-encryption-aws-kms-key-id": kms_alias,
        }
    }

def presign_get(
    resource: Resource,
    key: str,
    expires_in: int = 900,
    response_inline: bool = True,
    filename: Optional[str] = None,
    response_content_type: Optional[str] = None
) -> dict:
    bucket, _ = _bucket_and_kms(resource)
    client = s3_client()

    params = {"Bucket": bucket, "Key": key}
    if response_content_type:
        params["ResponseContentType"] = response_content_type
    if filename:
        disp = "inline" if response_inline else "attachment"
        params["ResponseContentDisposition"] = f'{disp}; filename="{filename}"'

    url = client.generate_presigned_url(
        "get_object",
        Params=params,
        ExpiresIn=expires_in
    )
    return {"download_url": url, "expires_in": expires_in}


def multipart_create(resource: Resource, key: str, content_type: str) -> dict:
    bucket, kms_alias = _bucket_and_kms(resource)
    client = s3_client()
    resp = client.create_multipart_upload(
        Bucket=bucket,
        Key=key,
        ContentType=content_type,
        ServerSideEncryption="aws:kms",
        SSEKMSKeyId=kms_alias,
    )
    return {"upload_id": resp["UploadId"]}

def multipart_sign_part(resource: Resource, key: str, upload_id: str, part_number: int, expires_in: int = 3600) -> str:
    bucket, _ = _bucket_and_kms(resource)
    client = s3_client()
    url = client.generate_presigned_url(
        "upload_part",
        Params={
            "Bucket": bucket,
            "Key": key,
            "UploadId": upload_id,
            "PartNumber": part_number,
        },
        ExpiresIn=expires_in,
    )
    return url

def multipart_complete(resource: Resource, key: str, upload_id: str, parts: list[dict]) -> dict:
    """
    parts: [{"ETag": "...","PartNumber": 1}, ...]
    """
    bucket, _ = _bucket_and_kms(resource)
    client = s3_client()
    client.complete_multipart_upload(
        Bucket=bucket,
        Key=key,
        UploadId=upload_id,
        MultipartUpload={"Parts": parts},
    )
    return {"ok": True}
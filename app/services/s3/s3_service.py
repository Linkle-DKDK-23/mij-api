import boto3
from typing import Literal
from .client import s3_client, VIDEO_BUCKET, IDENTITY_BUCKET, KMS_ALIAS_VIDEO, KMS_ALIAS_IDENTITY


Resource = Literal["video", "identity"]

def _bucket_and_kms(resource: Resource):
    """
    バケットとKMSキーを取得

    Args:
        resource (Resource): リソース
    """
    if resource == "video":
        return VIDEO_BUCKET, KMS_ALIAS_VIDEO
    elif resource == "identity":
        return IDENTITY_BUCKET, KMS_ALIAS_IDENTITY
    raise ValueError("unknown resource")

def bucket_exit_check(resource: Resource, key: str):

    """
    バケット存在確認

    Args:
        resource (Resource): リソース
        key (str): キー
    """
    bucket, _ = _bucket_and_kms(resource)
    client = s3_client()
    try:
        client.head_object(Bucket=bucket, Key=key)
    except Exception:
        return False
    return True


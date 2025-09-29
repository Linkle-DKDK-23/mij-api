import boto3
from typing import Literal
from .client import s3_client, KYC_BUCKET_NAME, KMS_ALIAS_KYC


Resource = Literal["identity"]

def _bucket_and_kms(resource: Resource):
    """
    バケットとKMSキーを取得

    Args:
        resource (Resource): リソース
    """
    if resource == "identity":
        return KYC_BUCKET_NAME, KMS_ALIAS_KYC
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


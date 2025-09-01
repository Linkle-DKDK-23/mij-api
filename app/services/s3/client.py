# app/services/s3/client.py
import os
from functools import lru_cache
import boto3
from botocore.config import Config

AWS_REGION = os.environ.get("AWS_REGION", "ap-northeast-1")

def s3_client():
    return boto3.client(
        "s3",
        region_name=AWS_REGION,
        endpoint_url=f"https://s3.{AWS_REGION}.amazonaws.com",
        config=Config(signature_version="s3v4")
    )

@lru_cache(maxsize=1)
def s3_client_for_mc():
    base = boto3.client("mediaconvert", region_name=AWS_REGION)
    ep = base.describe_endpoints(MaxResults=1)["Endpoints"][0]["Url"]
    return boto3.client("mediaconvert", region_name=AWS_REGION, endpoint_url=ep)
# ビデオ
VIDEO_BUCKET = os.environ.get("S3_BUCKET_NAME") 
IDENTITY_BUCKET   = os.environ.get("KYC_BUCKET_NAME") 

# 認証
KMS_ALIAS_VIDEO = os.environ.get("KMS_ALIAS_VIDEO") 
KMS_ALIAS_IDENTITY   = os.environ.get("KMS_ALIAS_KYC") 

# アカウント
ASSETS_BUCKET_NAME = os.environ.get("ASSETS_BUCKET_NAME")
KMS_ALIAS_ACCOUNT = os.environ.get("KMS_ALIAS_ASSET")

# ビデオバケット
INGEST_BUCKET = os.environ.get("INGEST_BUCKET_NAME") 
KMS_ALIAS_INGEST   = os.environ.get("KMS_ALIAS_INGEST") 

# メディアコンバート
MEDIA_BUCKET_NAME = os.environ.get("MEDIA_BUCKET_NAME")
KMS_ALIAS_MEDIA = os.environ.get("KMS_ALIAS_MEDIA")

MEDIACONVERT_ROLE_ARN = os.environ.get("MEDIACONVERT_ROLE_ARN")
OUTPUT_KMS_ARN = os.environ.get("OUTPUT_KMS_ARN")
# app/services/s3/client.py
import os
import boto3
from botocore.config import Config

AWS_REGION = os.environ.get("AWS_REGION", "ap-northeast-1")

def s3_client():
    return boto3.client(
        "s3",
        region_name=AWS_REGION,
        config=Config(signature_version="s3v4")
    )

# ビデオ
VIDEO_BUCKET = os.environ.get("S3_BUCKET_NAME") 
IDENTITY_BUCKET   = os.environ.get("KYC_BUCKET_NAME") 

# 認証
KMS_ALIAS_VIDEO = os.environ.get("KMS_ALIAS_VIDEO") 
KMS_ALIAS_IDENTITY   = os.environ.get("KMS_ALIAS_KYC") 

# アカウント
ASSETS_BUCKET_NAME = os.environ.get("ASSETS_BUCKET_NAME")
KMS_ALIAS_ACCOUNT = os.environ.get("KMS_ALIAS_ASSET")

INGEST_BUCKET = os.environ.get("INGEST_BUCKET_NAME") 
KMS_ALIAS_INGEST   = os.environ.get("KMS_ALIAS_INGEST") 
import boto3
import os
import uuid
from dotenv import load_dotenv
from app.schemas.video import UploadFile

load_dotenv()

AWS_REGION = os.environ.get("AWS_REGION", "ap-northeast-1")
S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]

# S3クライアントを初期化（グローバルで使い回せる）
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    region_name=AWS_REGION
)

def generate_presigned_url(filename: str, content_type: str) -> dict:
    """
    アップロード用プレシジョンURLを生成する

    Args:
        filename (str): ファイル名
        content_type (str): コンテントタイプ

    Returns:
        dict: プレシジョンURL
    """
    key = f"uploads/{filename}"
    url = s3_client.generate_presigned_url(
        "put_object",
        Params={"Bucket": S3_BUCKET_NAME, "Key": key, "ContentType": content_type},
        ExpiresIn=3600
    )
    return {
        "upload_url": url,
        "file_key": key
    }

def generate_play_url(file_key: str) -> str:
    """
    再生用プレシジョンURLを生成する

    Args:
        file_key (str): ファイルキー

    Returns:
        str: 再生用プレシジョンURL
    """
    url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": S3_BUCKET_NAME, "Key": file_key},
        ExpiresIn=3600,
    )
    return url
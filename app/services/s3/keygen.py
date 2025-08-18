# app/services/s3/keygen.py
import uuid
from datetime import datetime

def video_key(creator_id: str, filename: str) -> str:
    """
    ビデオキー生成

    Args:
        creator_id (str): クリエイターID
        filename (str): ファイル名

    Returns:
        str: ビデオキー
    """
    uid = uuid.uuid4()
    d = datetime.utcnow()
    return f"{creator_id}/videos/{d.year}/{d.month:02d}/{d.day:02d}/{uid}/raw/{filename}"

def identity_key(creator_id: str, submission_id: str, kind: str, ext: str) -> str:
    """
    身分証明書キー生成

    Args:
        creator_id (str): クリエイターID
        submission_id (str): 提出ID
        kind (str): 種類
        ext (str): 拡張子

    Returns:
        str: 身分証明書キー
    """
    return f"{creator_id}/identity/{submission_id}/{kind}.{ext}"


def account_asset_key(creator_id: str, kind: str, ext: str) -> str:
    """
    アバターキー生成

    Args:
        creator_id (str): クリエイターID
        filename (str): ファイル名
    Returns:
        str: アバターキー
    """
    return f"profiles/{creator_id}/{kind}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4()}.{ext}"
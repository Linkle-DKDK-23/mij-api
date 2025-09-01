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

def post_media_image_key(kind: str, creator_id: str, post_id: str, ext: str) -> str:
    """
    投稿メディア画像キー生成

    Args:
        kind: str 種類
        creator_id: str クリエイターID
        post_id: str 投稿ID
        ext: str 拡張子

    Returns:
        str: 投稿メディア画像キー
    """
    return f"post-media/{creator_id}/{kind}/{post_id}/{uuid.uuid4()}.{ext}"


def post_media_video_key(creator_id: str, post_id: str, ext: str, kind: str) -> str:
    """
    投稿メディアビデオキー生成

    Args:
        creator_id: str クリエイターID
        post_id: str 投稿ID
        ext: str 拡張子
        kind: str 種類

    Returns:
        str: 投稿メディアビデオキー
    """
    return f"post-media/{creator_id}/{kind}/{post_id}/{uuid.uuid4()}.{ext}"

def transcode_mc_key(creator_id: str, post_id: str, asset_id: str) -> str:
    """
    メディアコンバートキー生成

    Args:
        creator_id: str クリエイターID
        post_id: str 投稿ID
        ext: str 拡張子
        kind: str 種類

    Returns:
        str: メディアコンバートキー
    """
    return f"transcode-mc/{creator_id}/{post_id}/{asset_id}/preview/preview.mp4"


def transcode_mc_hls_prefix(creator_id: str, post_id: str, asset_id: str) -> str:
    """
    HLS 出力のプレフィックスを生成

    Args:
        creator_id: str クリエイターID
        post_id: str 投稿ID
        asset_id: str アセットID

    Returns:
        str: HLS 出力のプレフィックス
    """
    return f"transcode-mc/{creator_id}/{post_id}/{asset_id}/hls/"

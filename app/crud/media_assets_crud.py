from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.media_assets import MediaAssets
from app.models.posts import Posts
from app.constants.enums import MediaAssetKind

def create_media_asset(db: Session, media_asset_data: dict) -> MediaAssets:
    """
    メディアアセット作成

    Args:
        db (Session): データベースセッション
        media_asset (MediaAssets): メディアアセット

    Returns:
        MediaAssets: メディアアセット
    """
    db_media_asset = MediaAssets(**media_asset_data)
    db.add(db_media_asset)
    db.flush()
    return db_media_asset


def get_media_asset_by_post_id(db: Session, post_id: str) -> MediaAssets:
    """
    メディアアセット取得（postテーブルとJOINしてユーザーIDも取得）

    Args:
        db (Session): データベースセッション
        post_id (str): 投稿ID

    Returns:
        MediaAssets: メディアアセット（post情報も含む）
    """
    result = db.execute(
        select(
            MediaAssets.id,
            MediaAssets.post_id,
            MediaAssets.kind,
            MediaAssets.created_at,
            MediaAssets.storage_key,
            Posts.creator_user_id
        ).join(
            Posts, MediaAssets.post_id == Posts.id
        ).where(
            MediaAssets.post_id == post_id, 
            MediaAssets.kind.in_([
                MediaAssetKind.MAIN_VIDEO, 
                MediaAssetKind.SAMPLE_VIDEO, 
            ])
        )
    ).all()
    
    return result

def get_media_asset_by_id(db: Session, asset_id: str) -> MediaAssets:
    """
    メディアアセット取得
    """
    return db.query(MediaAssets).filter(MediaAssets.id == asset_id).first()
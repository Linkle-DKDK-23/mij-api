from sqlalchemy.orm import Session
from app.models.media_renditions import MediaRenditions

def create_media_rendition(db: Session, media_rendition: dict) -> MediaRenditions:
    """
    メディアレンディション作成
    """
    db_media_rendition = MediaRenditions(**media_rendition)
    db.add(db_media_rendition)
    db.flush()
    return db_media_rendition
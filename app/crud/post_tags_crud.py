from sqlalchemy.orm import Session
from app.models.tags import PostTags

def create_post_tag(db: Session, post_tag_data) -> PostTags:
    """
    投稿に紐づくタグを作成
    """
    db_post_tag = PostTags(**post_tag_data)
    db.add(db_post_tag)
    db.flush()
    return db_post_tag
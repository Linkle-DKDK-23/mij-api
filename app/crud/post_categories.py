from sqlalchemy.orm import Session
from app.models.post_categories import PostCategories

def create_post_category(db: Session, post_category_data) -> PostCategories:
    """
    投稿に紐づくカテゴリを作成
    """
    db_post_category = PostCategories(**post_category_data)
    db.add(db_post_category)
    db.flush()
    return db_post_category
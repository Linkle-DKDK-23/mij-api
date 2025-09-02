from sqlalchemy.orm import Session
from app.models.categories import Categories
from app.models.genres import Genres
from app.models.post_categories import PostCategories
from app.models.posts import Posts
from typing import List
from uuid import UUID
import random

def get_categories(db: Session) -> List[Categories]:
    return db.query(Categories).filter(Categories.is_active == True).order_by(Categories.sort_order).all()

def get_genres(db: Session) -> List[Genres]:
    return db.query(Genres).filter(Genres.is_active == True).order_by(Genres.sort_order).all()

def get_recommended_categories(db: Session, limit: int = 8) -> List[Categories]:
    categories = get_categories(db)
    return random.sample(categories, min(limit, len(categories)))

def get_recently_used_categories(db: Session, creator_user_id: UUID, limit: int = 10) -> List[Categories]:
    return db.query(Categories).join(PostCategories).join(Posts).filter(
        Posts.creator_user_id == creator_user_id,
        Categories.is_active == True
    ).order_by(PostCategories.created_at.desc()).limit(limit).all()

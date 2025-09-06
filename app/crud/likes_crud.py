from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.social import Likes
from app.models.posts import Posts
from uuid import UUID
from typing import List

def get_likes_count(db: Session, post_id: UUID) -> int:
    """
    いいね数を取得
    """
    likes_count = db.query(Likes).filter(Likes.post_id == post_id).count()
    return likes_count

def create_like(db: Session, user_id: UUID, post_id: UUID) -> Likes:
    """
    いいねを作成
    """
    like = Likes(
        user_id=user_id,
        post_id=post_id
    )
    db.add(like)
    db.commit()
    db.refresh(like)
    return like

def delete_like(db: Session, user_id: UUID, post_id: UUID) -> bool:
    """
    いいねを削除
    """
    like = (
        db.query(Likes)
        .filter(
            and_(
                Likes.user_id == user_id,
                Likes.post_id == post_id
            )
        )
        .first()
    )
    
    if like:
        db.delete(like)
        db.commit()
        return True
    
    return False

def is_liked(db: Session, user_id: UUID, post_id: UUID) -> bool:
    """
    ユーザーが投稿をいいねしているかチェック
    """
    like = (
        db.query(Likes)
        .filter(
            and_(
                Likes.user_id == user_id,
                Likes.post_id == post_id
            )
        )
        .first()
    )
    return like is not None

def get_liked_posts_by_user_id(
    db: Session, 
    user_id: UUID, 
    skip: int = 0, 
    limit: int = 20
) -> List[Posts]:
    """
    ユーザーがいいねした投稿一覧を取得
    """
    return (
        db.query(Posts)
        .join(Likes)
        .filter(Likes.user_id == user_id)
        .order_by(Likes.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def toggle_like(db: Session, user_id: UUID, post_id: UUID) -> dict:
    """
    いいねのトグル（追加/削除）
    """
    existing_like = (
        db.query(Likes)
        .filter(
            and_(
                Likes.user_id == user_id,
                Likes.post_id == post_id
            )
        )
        .first()
    )
    
    if existing_like:
        # いいね削除
        db.delete(existing_like)
        db.commit()
        return {"liked": False, "message": "いいねを取り消しました"}
    else:
        # いいね追加
        like = Likes(user_id=user_id, post_id=post_id)
        db.add(like)
        db.commit()
        return {"liked": True, "message": "いいねしました"}
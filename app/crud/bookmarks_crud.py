from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.social import Bookmarks
from app.models.posts import Posts
from uuid import UUID
from typing import List

def create_bookmark(db: Session, user_id: UUID, post_id: UUID) -> Bookmarks:
    """
    ブックマークを作成
    """
    bookmark = Bookmarks(
        user_id=user_id,
        post_id=post_id
    )
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    return bookmark

def delete_bookmark(db: Session, user_id: UUID, post_id: UUID) -> bool:
    """
    ブックマークを削除
    """
    bookmark = (
        db.query(Bookmarks)
        .filter(
            and_(
                Bookmarks.user_id == user_id,
                Bookmarks.post_id == post_id
            )
        )
        .first()
    )
    
    if bookmark:
        db.delete(bookmark)
        db.commit()
        return True
    
    return False

def is_bookmarked(db: Session, user_id: UUID, post_id: UUID) -> bool:
    """
    ユーザーが投稿をブックマークしているかチェック
    """
    bookmark = (
        db.query(Bookmarks)
        .filter(
            and_(
                Bookmarks.user_id == user_id,
                Bookmarks.post_id == post_id
            )
        )
        .first()
    )
    return bookmark is not None

def get_bookmarks_by_user_id(
    db: Session, 
    user_id: UUID, 
    skip: int = 0, 
    limit: int = 20
) -> List[Posts]:
    """
    ユーザーのブックマーク一覧を取得
    """
    return (
        db.query(Posts)
        .join(Bookmarks)
        .filter(Bookmarks.user_id == user_id)
        .order_by(Bookmarks.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_bookmarks_count_by_user_id(db: Session, user_id: UUID) -> int:
    """
    ユーザーのブックマーク数を取得
    """
    return (
        db.query(Bookmarks)
        .filter(Bookmarks.user_id == user_id)
        .count()
    )

def toggle_bookmark(db: Session, user_id: UUID, post_id: UUID) -> dict:
    """
    ブックマークのトグル（追加/削除）
    """
    existing_bookmark = (
        db.query(Bookmarks)
        .filter(
            and_(
                Bookmarks.user_id == user_id,
                Bookmarks.post_id == post_id
            )
        )
        .first()
    )
    
    if existing_bookmark:
        # ブックマーク削除
        db.delete(existing_bookmark)
        db.commit()
        return {"bookmarked": False, "message": "ブックマークを削除しました"}
    else:
        # ブックマーク追加
        bookmark = Bookmarks(user_id=user_id, post_id=post_id)
        db.add(bookmark)
        db.commit()
        return {"bookmarked": True, "message": "ブックマークに追加しました"}
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.social import Follows
from app.models.user import Users
from uuid import UUID
from typing import List

def get_follower_count(db: Session, user_id: UUID) -> dict:
    """
    フォロワー数を取得
    """
    followers_count = db.query(Follows).filter(Follows.creator_user_id == user_id).count()
    following_count = db.query(Follows).filter(Follows.follower_user_id == user_id).count()
    return {
        "followers_count": followers_count,
        "following_count": following_count
    }

def create_follow(db: Session, follower_user_id: UUID, creator_user_id: UUID) -> Follows:
    """
    フォロー関係を作成
    """
    follow = Follows(
        follower_user_id=follower_user_id,
        creator_user_id=creator_user_id
    )
    db.add(follow)
    db.commit()
    db.refresh(follow)
    return follow

def delete_follow(db: Session, follower_user_id: UUID, creator_user_id: UUID) -> bool:
    """
    フォロー関係を削除
    """
    follow = (
        db.query(Follows)
        .filter(
            and_(
                Follows.follower_user_id == follower_user_id,
                Follows.creator_user_id == creator_user_id
            )
        )
        .first()
    )
    
    if follow:
        db.delete(follow)
        db.commit()
        return True
    
    return False

def is_following(db: Session, follower_user_id: UUID, creator_user_id: UUID) -> bool:
    """
    フォロー関係があるかチェック
    """
    follow = (
        db.query(Follows)
        .filter(
            and_(
                Follows.follower_user_id == follower_user_id,
                Follows.creator_user_id == creator_user_id
            )
        )
        .first()
    )
    return follow is not None

def get_followers(
    db: Session, 
    user_id: UUID, 
    skip: int = 0, 
    limit: int = 20
) -> List[Users]:
    """
    フォロワー一覧を取得
    """
    return (
        db.query(Users)
        .join(Follows, Follows.follower_user_id == Users.id)
        .filter(Follows.creator_user_id == user_id)
        .order_by(Follows.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_following(
    db: Session, 
    user_id: UUID, 
    skip: int = 0, 
    limit: int = 20
) -> List[Users]:
    """
    フォロー中のユーザー一覧を取得
    """
    return (
        db.query(Users)
        .join(Follows, Follows.creator_user_id == Users.id)
        .filter(Follows.follower_user_id == user_id)
        .order_by(Follows.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def toggle_follow(db: Session, follower_user_id: UUID, creator_user_id: UUID) -> dict:
    """
    フォローのトグル（フォロー/フォロー解除）
    """
    if follower_user_id == creator_user_id:
        return {"following": False, "message": "自分自身をフォローすることはできません"}
    
    existing_follow = (
        db.query(Follows)
        .filter(
            and_(
                Follows.follower_user_id == follower_user_id,
                Follows.creator_user_id == creator_user_id
            )
        )
        .first()
    )
    
    if existing_follow:
        # フォロー解除
        db.delete(existing_follow)
        db.commit()
        return {"following": False, "message": "フォローを解除しました"}
    else:
        # フォロー
        follow = Follows(follower_user_id=follower_user_id, creator_user_id=creator_user_id)
        db.add(follow)
        db.commit()
        return {"following": True, "message": "フォローしました"}

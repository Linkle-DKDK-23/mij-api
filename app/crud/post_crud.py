from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.posts import Posts
from app.models.social import Likes
from uuid import UUID
from app.constants.enums import PostStatus
from app.schemas.post import PostCreateRequest

def get_total_likes_by_user_id(db: Session, user_id: UUID) -> int:
    """
    ユーザーの投稿についた総合いいね数を取得
    """
    
    # いいねテーブルと結合していいね数を取得
    total_likes = (
        db.query(func.count(Likes.post_id))
        .join(Posts, Likes.post_id == Posts.id)
        .filter(Posts.creator_user_id == user_id)
        .filter(Posts.deleted_at.is_(None))  # 削除されていない投稿のみ
        .scalar()
    )
    
    return total_likes or 0

def get_posts_count_by_user_id(db: Session, user_id: UUID) -> dict:
    """
    各ステータスの投稿数を取得
    """
    
    # 審査中
    peding_posts_count = db.query(Posts).filter(Posts.creator_user_id == user_id).filter(Posts.deleted_at.is_(None)).filter(Posts.status == PostStatus.PENDING).count()

    # 修正
    rejected_posts_count = db.query(Posts).filter(Posts.creator_user_id == user_id).filter(Posts.deleted_at.is_(None)).filter(Posts.status == PostStatus.REJECTED).count()

    # 非公開
    unpublished_posts_count = db.query(Posts).filter(Posts.creator_user_id == user_id).filter(Posts.deleted_at.is_(None)).filter(Posts.status == PostStatus.UNPUBLISHED).count()

    # 削除
    deleted_posts_count = db.query(Posts).filter(Posts.creator_user_id == user_id).filter(Posts.deleted_at.is_(None)).filter(Posts.status == PostStatus.DELETED).count()

    # 公開
    approved_posts_count = db.query(Posts).filter(Posts.creator_user_id == user_id).filter(Posts.deleted_at.is_(None)).filter(Posts.status == PostStatus.APPROVED).count()

    return {
        "peding_posts_count": peding_posts_count,
        "rejected_posts_count": rejected_posts_count,
        "unpublished_posts_count": unpublished_posts_count,
        "deleted_posts_count": deleted_posts_count,
        "approved_posts_count": approved_posts_count
    }

def create_post(db: Session, post_data: dict):
    """
    投稿を作成
    """
    post = Posts(**post_data)
    db.add(post)
    db.flush()
    return post
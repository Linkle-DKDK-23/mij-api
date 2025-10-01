from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import Users
from app.schemas.user import UserCreate
from app.core.security import hash_password
from sqlalchemy import select, desc, func
from app.constants.enums import (
    AccountType, 
    AccountStatus
)
from app.crud.profile_crud import get_profile_by_username
from app.models.posts import Posts
from app.models.plans import Plans, PostPlans
from app.models.orders import Orders, OrderItems
from app.models.media_assets import MediaAssets
from app.models.social import Likes, Follows
from app.models.prices import Prices
from app.constants.enums import PostStatus, MediaAssetKind, PlanStatus


def create_user(db: Session, user_create: UserCreate) -> Users:
    """
    ユーザーを作成する

    Args:
        db: データベースセッション
        user_create: ユーザー作成情報
    """
    # ランダム文字列5文字作成
    db_user = Users(
        profile_name=user_create.name,
        email=user_create.email,
        password_hash=hash_password(user_create.password),
        role=AccountType.GENERAL_USER,
        status=AccountStatus.ACTIVE
    )
    db.add(db_user)
    db.flush()
    return db_user

def check_email_exists(db: Session, email: str) -> bool:
    """
    メールアドレスの重複チェック

    Args:
        db (Session): データベースセッション
        email (str): メールアドレス

    Returns:
        bool: 重複している場合はTrue、重複していない場合はFalse
    """
    result = db.query(Users).filter(Users.email == email).first()
    return result is not None

def check_profile_name_exists(db: Session, profile_name: str) -> bool:
    """
    プロファイル名の重複チェック

    Args:
        db (Session): データベースセッション
        profile_name (str): プロファイル名

    Returns:
        bool: 重複している場合はTrue、重複していない場合はFalse
    """
    result = db.query(Users).filter(Users.profile_name == profile_name).first()
    return result is not None

def get_user_by_email(db: Session, email: str) -> Users:
    """
    メールアドレスによるユーザー取得

    Args:
        db (Session): データベースセッション
        email (str): メールアドレス

    Returns:
        Users: ユーザー情報
    """
    return db.scalar(select(Users).where(Users.email == email))

def get_user_by_id(db: Session, user_id: str) -> Users:
    """
    ユーザーIDによるユーザー取得

    Args:
        db (Session): データベースセッション
        user_id (str): ユーザーID

    Returns:
        Users: ユーザー情報
    """
    return db.get(Users, user_id)

def update_user(db: Session, user_id: str, profile_name: str) -> Users:
    """
    ユーザーを更新
    """
    user = get_user_by_id(db, user_id)
    user.profile_name = profile_name
    db.add(user)
    db.flush()
    return user

def get_user_profile_by_username(db: Session, username: str) -> dict:
    """
    ユーザー名によるユーザープロフィール取得（関連データ含む）
    """


    profile = get_profile_by_username(db, username)

    if not profile:
        return None
    
    user = get_user_by_id(db, profile.user_id)
    
    posts = (
        db.query(
            Posts, 
            func.count(Likes.post_id).label('likes_count'),
            MediaAssets.storage_key.label('thumbnail_key')
        )
        .outerjoin(Likes, Posts.id == Likes.post_id)
        .join(Users, Posts.creator_user_id == Users.id)
        .outerjoin(MediaAssets, (Posts.id == MediaAssets.post_id) & (MediaAssets.kind == MediaAssetKind.THUMBNAIL))
        .filter(Posts.creator_user_id == user.id)
        .filter(Posts.deleted_at.is_(None))
        .filter(Posts.status == PostStatus.APPROVED)
        .group_by(Posts.id, MediaAssets.storage_key)  # GROUP BY句を追加
        .order_by(desc(Posts.created_at))
        .all()
    )
    
    plans = db.query(Plans).filter(Plans.creator_user_id == user.id).filter(Plans.type == PlanStatus.PLAN).filter(Plans.deleted_at.is_(None)).all()
    
    individual_purchases = (
        db.query(
            Posts, 
            func.count(Likes.post_id).label('likes_count'),
            MediaAssets.storage_key.label('thumbnail_key')
        )
        .outerjoin(Likes, Posts.id == Likes.post_id)
        .join(Users, Posts.creator_user_id == Users.id)
        .join(PostPlans, Posts.id == PostPlans.post_id)  # PostPlansテーブルを通じて結合
        .join(Plans, PostPlans.plan_id == Plans.id)  # Plansテーブルと結合
        .outerjoin(MediaAssets, (Posts.id == MediaAssets.post_id) & (MediaAssets.kind == MediaAssetKind.THUMBNAIL))
        .filter(Posts.creator_user_id == user.id)
        .filter(Posts.deleted_at.is_(None))
        .filter(Plans.type == PlanStatus.SINGLE)  # typeが1（SINGLE）のもののみ
        .filter(Plans.deleted_at.is_(None))  # 削除されていないプランのみ
        .filter(Posts.status == PostStatus.APPROVED)
        .group_by(Posts.id, MediaAssets.storage_key)
        .order_by(desc(Posts.created_at))
        .all()
    )
    
    gacha_items = db.query(OrderItems).join(Orders).filter(Orders.user_id == user.id).filter(OrderItems.item_type == 2).all()
    
    return {
        "user": user,
        "profile": profile,
        "posts": posts,
        "plans": plans,
        "individual_purchases": individual_purchases,
        "gacha_items": gacha_items
    }

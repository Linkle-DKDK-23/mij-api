from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, asc
from datetime import datetime
from uuid import UUID

from app.models.user import Users
from app.models.creators import Creators
from app.models.identity import IdentityVerifications
from app.models.posts import Posts
from app.models.profiles import Profiles
from app.models.orders import Orders
from app.models.subscriptions import Subscriptions
from app.models.media_assets import MediaAssets
from app.models.media_rendition_jobs import MediaRenditionJobs
import os

CDN_URL = os.getenv("CDN_BASE_URL")



"""管理機能用のCRUD操作クラス"""


def get_dashboard_info(db: Session) -> Dict[str, Any]:
    """
    ダッシュボード統計情報を取得
    
    Args:
        db: データベースセッション
        
    Returns:
        Dict[str, Any]: 統計情報
    """
    try:
        # 基本統計
        total_users = db.query(Users).count()
        total_posts = db.query(Posts).count()
        
        # 身分証申請中件数（status=1が申請中）
        pending_identity_verifications = db.query(IdentityVerifications).filter(
            IdentityVerifications.status == 1
        ).count()
        
        # クリエイター申請中件数（status=1が申請中）
        pending_creator_applications = db.query(Creators).filter(
            Creators.status == 1
        ).count()
        
        # 投稿申請中件数（審査待ちの投稿があると仮定してstatus=1）
        pending_post_reviews = db.query(Posts).filter(
            Posts.status == 1
        ).count()
        
        # 月間売上（仮の値 - 実際のOrdersテーブルから計算する場合）
        monthly_revenue = 100000
        
        # アクティブな購読数
        active_subscriptions = db.query(Subscriptions).filter(
            Subscriptions.status == 1  # アクティブな購読
        ).count()
        
        return {
            "total_users": total_users,
            "total_posts": total_posts,
            "pending_identity_verifications": pending_identity_verifications,
            "pending_creator_applications": pending_creator_applications,
            "pending_post_reviews": pending_post_reviews,
            "monthly_revenue": monthly_revenue,
            "active_subscriptions": active_subscriptions
        }
    except Exception as e:
        print(f"Dashboard stats error: {e}")
        # エラー時はデフォルト値を返す
        return {
            "total_users": 0,
            "total_posts": 0,
            "pending_identity_verifications": 0,
            "pending_creator_applications": 0,
            "pending_post_reviews": 0,
            "monthly_revenue": 0,
            "active_subscriptions": 0
        }


def get_users_paginated(
    db: Session,
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    role: Optional[str] = None,
    sort: str = "created_at_desc"
) -> tuple[List[Users], int]:
    """
    ページネーション付きユーザー一覧を取得
    
    Args:
        db: データベースセッション
        page: ページ番号
        limit: 1ページあたりの件数
        search: 検索クエリ
        role: ロールフィルタ
        sort: ソート順
        
    Returns:
        tuple[List[Users], int]: (ユーザーリスト, 総件数)
    """
    skip = (page - 1) * limit
    
    query = db.query(Users).options(joinedload(Users.profile))
    
    if search:
        query = query.join(Profiles).filter(
            (Profiles.display_name.ilike(f"%{search}%")) |
            (Users.email.ilike(f"%{search}%"))
        )
    
    if role:
        role_map = {"user": 1, "creator": 2, "admin": 3}
        query = query.filter(Users.role == role_map.get(role))
    
    # ソート処理
    if sort == "created_at_desc":
        query = query.order_by(desc(Users.created_at))
    elif sort == "created_at_asc":
        query = query.order_by(asc(Users.created_at))
    elif sort == "display_name_asc":
        query = query.join(Profiles).order_by(asc(Profiles.display_name))
    elif sort == "display_name_desc":
        query = query.join(Profiles).order_by(desc(Profiles.display_name))
    elif sort == "email_asc":
        query = query.order_by(asc(Users.email))
    else:
        query = query.order_by(desc(Users.created_at))
    
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    
    return users, total


def get_creator_applications_paginated(
    db: Session,
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    status: Optional[str] = None,
    sort: str = "created_at_desc"
) -> tuple[List[Creators], int]:
    """
    ページネーション付きクリエイター申請一覧を取得
    
    Args:
        db: データベースセッション
        page: ページ番号
        limit: 1ページあたりの件数
        search: 検索クエリ
        status: ステータスフィルタ
        sort: ソート順
        
    Returns:
        tuple[List[Creators], int]: (申請リスト, 総件数)
    """
    skip = (page - 1) * limit
    
    query = db.query(Creators).join(Users).options(joinedload(Creators.user))
    
    if search:
        query = query.join(Profiles).filter(
            (Profiles.display_name.ilike(f"%{search}%")) |
            (Users.email.ilike(f"%{search}%"))
        )
    
    if status:
        status_map = {"pending": 1, "approved": 2, "rejected": 3}
        query = query.filter(Creators.status == status_map.get(status, 1))
    
    # ソート処理
    if sort == "created_at_desc":
        query = query.order_by(desc(Creators.created_at))
    elif sort == "created_at_asc":
        query = query.order_by(asc(Creators.created_at))
    elif sort == "user_name_asc":
        query = query.join(Profiles).order_by(asc(Profiles.display_name))
    elif sort == "user_name_desc":
        query = query.join(Profiles).order_by(desc(Profiles.display_name))
    else:
        query = query.order_by(desc(Creators.created_at))
    
    total = query.count()
    applications = query.offset(skip).limit(limit).all()
    
    return applications, total


def get_identity_verifications_paginated(
    db: Session,
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    status: Optional[str] = None,
    sort: str = "created_at_desc"
) -> tuple[List[IdentityVerifications], int]:
    """
    ページネーション付き身分証明審査一覧を取得
    
    Args:
        db: データベースセッション
        page: ページ番号
        limit: 1ページあたりの件数
        search: 検索クエリ
        status: ステータスフィルタ
        sort: ソート順
        
    Returns:
        tuple[List[IdentityVerifications], int]: (審査リスト, 総件数)
    """
    skip = (page - 1) * limit
    
    query = db.query(IdentityVerifications).join(Users).options(joinedload(IdentityVerifications.user))
    
    if search:
        query = query.join(Profiles).filter(
            (Profiles.display_name.ilike(f"%{search}%")) |
            (Users.email.ilike(f"%{search}%"))
        )
    
    if status:
        status_map = {"pending": 1, "approved": 2, "rejected": 3}
        query = query.filter(IdentityVerifications.status == status_map.get(status, 1))
    
    # ソート処理
    if sort == "created_at_desc":
        query = query.order_by(desc(IdentityVerifications.created_at))
    elif sort == "created_at_asc":
        query = query.order_by(asc(IdentityVerifications.created_at))
    elif sort == "user_name_asc":
        query = query.join(Profiles).order_by(asc(Profiles.display_name))
    elif sort == "user_name_desc":
        query = query.join(Profiles).order_by(desc(Profiles.display_name))
    else:
        query = query.order_by(desc(IdentityVerifications.created_at))
    
    total = query.count()
    verifications = query.offset(skip).limit(limit).all()
    
    return verifications, total


def get_posts_paginated(
    db: Session,
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    status: Optional[str] = None,
    sort: str = "created_at_desc"
) -> tuple[List[Posts], int]:
    """
    ページネーション付き投稿一覧を取得
    
    Args:
        db: データベースセッション
        page: ページ番号
        limit: 1ページあたりの件数
        search: 検索クエリ
        status: ステータスフィルタ
        sort: ソート順
        
    Returns:
        tuple[List[Posts], int]: (投稿リスト, 総件数)
    """
    skip = (page - 1) * limit
    
    query = db.query(Posts).join(Users, Posts.creator_user_id == Users.id).options(joinedload(Posts.creator))
    
    if search:
        query = query.filter(
            Posts.description.ilike(f"%{search}%")
        )
    
    if status:
        status_map = {"draft": 1, "published": 2, "archived": 3}
        query = query.filter(Posts.status == status_map.get(status, 2))
    
    # ソート処理
    if sort == "created_at_desc":
        query = query.order_by(desc(Posts.created_at))
    elif sort == "created_at_asc":
        query = query.order_by(asc(Posts.created_at))
    elif sort == "description_asc":
        query = query.order_by(asc(Posts.description))
    elif sort == "description_desc":
        query = query.order_by(desc(Posts.description))
    else:
        query = query.order_by(desc(Posts.created_at))
    
    total = query.count()
    posts = query.offset(skip).limit(limit).all()
    
    return posts, total


def update_user_status(db: Session, user_id: str, status: str) -> bool:
    """
    ユーザーのステータスを更新
    
    Args:
        db: データベースセッション
        user_id: ユーザーID
        status: 新しいステータス
        
    Returns:
        bool: 更新成功フラグ
    """
    try:
        user = db.query(Users).filter(Users.id == user_id).first()
        if not user:
            return False
        
        # ステータス更新（実装に応じて調整）
        user.status = 2 if status == "suspended" else 1
        user.updated_at = datetime.utcnow()
        db.commit()
        return True
    except Exception as e:
        print(f"Update user status error: {e}")
        db.rollback()
        return False


def update_creator_application_status(db: Session, application_id: str, status: str) -> bool:
    """
    クリエイター申請のステータスを更新
    
    Args:
        db: データベースセッション
        application_id: 申請ID
        status: 新しいステータス (approved/rejected)
        
    Returns:
        bool: 更新成功フラグ
    """
    try:
        application = db.query(Creators).filter(Creators.id == application_id).first()
        if not application or application.status != 1:  # 1 = pending
            return False
        
        # 申請ステータス更新
        status_map = {"approved": 2, "rejected": 3}
        application.status = status_map[status]
        application.updated_at = datetime.utcnow()
        
        # 承認の場合、ユーザーのロールをクリエイターに更新
        if status == "approved":
            user = db.query(Users).filter(Users.id == application.user_id).first()
            if user:
                user.role = 2  # 2 = creator
                user.updated_at = datetime.utcnow()
        
        db.commit()
        return True
    except Exception as e:
        print(f"Update creator application status error: {e}")
        db.rollback()
        return False


def update_identity_verification_status(db: Session, verification_id: str, status: str) -> bool:
    """
    身分証明のステータスを更新
    
    Args:
        db: データベースセッション
        verification_id: 審査ID
        status: 新しいステータス (approved/rejected)
        
    Returns:
        bool: 更新成功フラグ
    """
    try:
        verification = db.query(IdentityVerifications).filter(
            IdentityVerifications.id == verification_id
        ).first()
        if not verification or verification.status != 1:  # 1 = pending
            return False
        
        # 審査ステータス更新
        status_map = {"approved": 2, "rejected": 3}
        verification.status = status_map[status]
        verification.updated_at = datetime.utcnow()
        
        db.commit()
        return True
    except Exception as e:
        print(f"Update identity verification status error: {e}")
        db.rollback()
        return False


def update_post_status(db: Session, post_id: str, status: str) -> bool:
    """
    投稿のステータスを更新
    
    Args:
        db: データベースセッション
        post_id: 投稿ID
        status: 新しいステータス
        
    Returns:
        bool: 更新成功フラグ
    """
    try:
        post = db.query(Posts).filter(Posts.id == post_id).first()
        if not post:
            return False
        
        status_map = {"published": 2, "archived": 3, "draft": 1}
        post.status = status_map.get(status, 2)
        post.updated_at = datetime.utcnow()
        
        db.commit()
        return True
    except Exception as e:
        print(f"Update post status error: {e}")
        db.rollback()
        return False


def get_post_by_id(db: Session, post_id: str) -> Dict[str, Any]:
    """
    投稿IDをキーにして投稿情報、ユーザー情報、メディア情報を取得
    """
    try:
        # UUIDに変換
        post_uuid = UUID(post_id)
    except ValueError:
        return None

    # 投稿情報と関連データを取得
    result = (
        db.query(
            Posts,
            Users,
            Profiles,
            MediaAssets,
            MediaRenditionJobs.output_key.label('rendition_output_key')
        )
        .join(Users, Posts.creator_user_id == Users.id)
        .join(Profiles, Users.id == Profiles.user_id)
        .outerjoin(MediaAssets, Posts.id == MediaAssets.post_id)
        .outerjoin(MediaRenditionJobs, MediaAssets.id == MediaRenditionJobs.asset_id)
        .filter(Posts.id == post_uuid)
        .filter(Posts.deleted_at.is_(None))
        .all()
    )

    if not result:
        return None

    # 最初のレコードから基本情報を取得
    first_row = result[0]
    post = first_row.Posts
    user = first_row.Users
    profile = first_row.Profiles

    # メディアアセット情報を整理
    media_assets = []
    rendition_jobs = []

    for row in result:
        if row.MediaAssets:
            media_asset = {
                'id': str(row.MediaAssets.id),
                'post_id': str(row.MediaAssets.post_id),
                'kind': row.MediaAssets.kind,
                'storage_key': row.MediaAssets.storage_key,
                'file_size': row.MediaAssets.bytes,
                'duration': float(row.MediaAssets.duration_sec) if row.MediaAssets.duration_sec else None,
                'width': row.MediaAssets.width,
                'height': row.MediaAssets.height,
                'created_at': row.MediaAssets.created_at.isoformat() if row.MediaAssets.created_at else None,
                'updated_at': None
            }
            
            # 重複を避けるため、既に存在するかチェック
            if not any(ma['id'] == media_asset['id'] for ma in media_assets):
                media_assets.append(media_asset)

        if row.rendition_output_key:
            rendition_job = {
                'output_key': row.rendition_output_key
            }
            
            # 重複を避けるため、既に存在するかチェック
            if not any(rj['output_key'] == rendition_job['output_key'] for rj in rendition_jobs):
                rendition_jobs.append(rendition_job)

    # CDN_URLを取得
    from os import getenv

    CDN_URL = getenv("CDN_BASE_URL", "")
    MEDIA_ASSETS_CDN_URL = getenv("MEDIA_CDN_URL", "")

    # 指定された内容を返却
    return {
        # 投稿情報
        'id': str(post.id),
        'description': post.description,
        'status': post.status,
        'created_at': post.created_at.isoformat() if post.created_at else None,
        # ユーザー情報
        'user_id': str(user.id),
        'user_slug': user.slug,
        # プロフィール情報
        'profile_display_name': profile.display_name,
        'profile_avatar_url': f"{CDN_URL}/{profile.avatar_url}" if profile.avatar_url else None,
        'post_type': post.post_type,
        # メディアアセット情報
        'media_assets': {
            ma['id']: {
                'kind': ma['kind'],
                'storage_key': ma['storage_key']
            } 
            for ma in media_assets if ma['storage_key']
        }  # メディアアセットIDをキー、kindとstorage_keyを含む辞書を値とする辞書
    }

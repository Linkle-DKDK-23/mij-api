from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from uuid import UUID
from os import getenv
from app.db.base import get_db
from app.deps.auth import get_current_admin_user
from app.schemas.admin import (
    AdminDashboardStats,
    AdminCreatorApplicationResponse,
    AdminIdentityVerificationResponse,
    AdminPostResponse,
    AdminUserResponse,
    AdminSalesData,
    CreatorApplicationReview,
    IdentityVerificationReview,
    PaginatedResponse,
    CreateUserRequest,
    AdminPostDetailResponse
)
from app.models.user import Users
from app.models.creators import Creators
from app.models.identity import IdentityVerifications
from app.models.posts import Posts
from app.models.profiles import Profiles
from app.core.security import hash_password
from app.crud.admin_crud import (
    get_dashboard_info,
    get_users_paginated,
    update_user_status,
    get_creator_applications_paginated,
    update_creator_application_status,
    get_identity_verifications_paginated,
    update_identity_verification_status,
    get_posts_paginated,
    update_post_status,
    get_post_by_id,
)
from app.services.s3.presign import presign_get
from app.constants.enums import MediaAssetKind

router = APIRouter()

@router.get("/dashboard/stats", response_model=AdminDashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_admin: Users = Depends(get_current_admin_user)
):
    """管理者ダッシュボード統計情報を取得"""
    
    # CRUDクラスから統計情報を取得
    stats = get_dashboard_info(db)
    
    return AdminDashboardStats(
        total_users=stats["total_users"],
        pending_creator_applications=stats["pending_creator_applications"],
        pending_identity_verifications=stats["pending_identity_verifications"],
        pending_post_reviews=stats["pending_post_reviews"],
        total_posts=stats["total_posts"],
        monthly_revenue=stats["monthly_revenue"],
        active_subscriptions=stats["active_subscriptions"]
    )

@router.get("/users", response_model=PaginatedResponse[AdminUserResponse])
def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    sort: Optional[str] = "created_at_desc",
    db: Session = Depends(get_db),
    current_admin: Users = Depends(get_current_admin_user)
):
    """ユーザー一覧を取得"""
    
    users, total = get_users_paginated(
        db=db,
        page=page,
        limit=limit,
        search=search,
        role=role,
        sort=sort
    )
    
    return PaginatedResponse(
        data=[AdminUserResponse.from_orm(user) for user in users],
        total=total,
        page=page,
        limit=limit,
        total_pages=(total + limit - 1) // limit if total > 0 else 1
    )

@router.patch("/users/{user_id}/status")
def update_user_status(
    user_id: str,
    status: str,
    db: Session = Depends(get_db),
    current_admin: Users = Depends(get_current_admin_user)
):
    """ユーザーのステータスを更新"""
    
    success = update_user_status(db, user_id, status)
    if not success:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    
    return {"message": "ユーザーステータスを更新しました"}

@router.post("/users", response_model=AdminUserResponse)
def create_user(
    user_data: CreateUserRequest,
    db: Session = Depends(get_db),
):
    """新しいユーザーを作成"""

    try:
    
    # メールアドレスの重複チェック
        existing_user = db.query(Users).filter(Users.email == user_data.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="このメールアドレスは既に使用されています")
        
        # ユーザー作成
        hashed_password = hash_password(user_data.password)
        
        # role の文字列を数値に変換
        role_map = {"user": 1, "creator": 2, "admin": 3}
        role_value = role_map.get(user_data.role, 1)
        
        new_user = Users(
            email=user_data.email,
            profile_name=user_data.username,
            password_hash=hashed_password,
            role=role_value,
            status=1,  # active
            email_verified_at=datetime.utcnow()  # 管理者作成ユーザーは確認済み
        )
        
        db.add(new_user)
        db.flush()  # ユーザーIDを取得するためにflush
        
        # プロフィール作成
        new_profile = Profiles(
            user_id=new_user.id,
            username=user_data.username,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_profile)
        db.commit()
        db.refresh(new_user)
        
        return AdminUserResponse.from_orm(new_user)
    except Exception as e:
        print("エラーが発生しました", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-test-admin")
def create_test_admin(
    db: Session = Depends(get_db)
):
    """テスト用管理者ユーザーを作成"""
    
    try:
        # 既存の管理者ユーザーをチェック
        existing_admin = db.query(Users).filter(Users.email == "admin@test.com").first()
        if existing_admin:
            return {"message": "テスト管理者は既に存在しています", "email": "admin@test.com"}
        
        # 管理者ユーザー作成
        hashed_password = hash_password("admin123")
        
        test_admin = Users(
            email="admin@test.com",
            profile_name="test_admin",
            password_hash=hashed_password,
            role=3,  # admin
            status=1,  # active
            email_verified_at=datetime.utcnow()
        )
        
        db.add(test_admin)
        db.flush()
        
        # プロフィール作成
        admin_profile = Profiles(
            user_id=test_admin.id,
            username="Test Admin",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(admin_profile)
        db.commit()
        
        return {
            "message": "テスト管理者を作成しました", 
            "email": "admin@test.com", 
            "password": "admin123"
        }
        
    except Exception as e:
        db.rollback()
        print("管理者作成エラー:", e)
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/creator-applications", response_model=PaginatedResponse[AdminCreatorApplicationResponse])
def get_creator_applications(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    sort: Optional[str] = "created_at_desc",
    db: Session = Depends(get_db),
    current_admin: Users = Depends(get_current_admin_user)
):
    """クリエイター申請一覧を取得"""
    
    applications, total = get_creator_applications_paginated(
        db=db,
        page=page,
        limit=limit,
        search=search,
        status=status,
        sort=sort
    )
    
    return PaginatedResponse(
        data=[AdminCreatorApplicationResponse.from_orm(app) for app in applications],
        total=total,
        page=page,
        limit=limit,
        total_pages=(total + limit - 1) // limit if total > 0 else 1
    )

@router.get("/creator-applications/{application_id}", response_model=AdminCreatorApplicationResponse)
def get_creator_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_admin: Users = Depends(get_current_admin_user)
):
    """クリエイター申請詳細を取得"""
    
    application = db.query(Creators).filter(Creators.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="申請が見つかりません")
    
    return AdminCreatorApplicationResponse.from_orm(application)

@router.patch("/creator-applications/{application_id}/review")
def review_creator_application(
    application_id: str,
    review: CreatorApplicationReview,
    db: Session = Depends(get_db),
    current_admin: Users = Depends(get_current_admin_user)
):
    """クリエイター申請を審査"""
    
    success = update_creator_application_status(db, application_id, review.status)
    if not success:
        raise HTTPException(status_code=404, detail="申請が見つかりませんまたは既に審査済みです")
    
    return {"message": "申請審査を完了しました"}

@router.get("/identity-verifications", response_model=PaginatedResponse[AdminIdentityVerificationResponse])
def get_identity_verifications(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    sort: Optional[str] = "created_at_desc",
    db: Session = Depends(get_db),
    current_admin: Users = Depends(get_current_admin_user)
):
    """身分証明審査一覧を取得"""
    
    verifications, total = get_identity_verifications_paginated(
        db=db,
        page=page,
        limit=limit,
        search=search,
        status=status,
        sort=sort
    )
    
    return PaginatedResponse(
        data=[AdminIdentityVerificationResponse.from_orm(v) for v in verifications],
        total=total,
        page=page,
        limit=limit,
        total_pages=(total + limit - 1) // limit if total > 0 else 1
    )

@router.get("/identity-verifications/{verification_id}", response_model=AdminIdentityVerificationResponse)
def get_identity_verification(
    verification_id: str,
    db: Session = Depends(get_db),
    current_admin: Users = Depends(get_current_admin_user)
):
    """身分証明審査詳細を取得"""
    
    verification = db.query(IdentityVerifications).filter(IdentityVerifications.id == verification_id).first()
    if not verification:
        raise HTTPException(status_code=404, detail="審査が見つかりません")
    
    return AdminIdentityVerificationResponse.from_orm(verification)

@router.patch("/identity-verifications/{verification_id}/review")
def review_identity_verification(
    verification_id: str,
    review: IdentityVerificationReview,
    db: Session = Depends(get_db),
    current_admin: Users = Depends(get_current_admin_user)
):
    """身分証明を審査"""
    
    success = update_identity_verification_status(db, verification_id, review.status)
    if not success:
        raise HTTPException(status_code=404, detail="審査が見つかりませんまたは既に完了済みです")
    
    return {"message": "身分証明審査を完了しました"}

@router.get("/posts", response_model=PaginatedResponse[AdminPostResponse])
def get_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    sort: Optional[str] = "created_at_desc",
    db: Session = Depends(get_db),
    current_admin: Users = Depends(get_current_admin_user)
):
    """投稿一覧を取得"""
    
    posts, total = get_posts_paginated(
        db=db,
        page=page,
        limit=limit,
        search=search,
        status=status,
        sort=sort
    )
    
    return PaginatedResponse(
        data=[AdminPostResponse.from_orm(post) for post in posts],
        total=total,
        page=page,
        limit=limit,
        total_pages=(total + limit - 1) // limit if total > 0 else 1
    )

@router.patch("/posts/{post_id}/status")
def update_post_status(
    post_id: str,
    status: str,
    db: Session = Depends(get_db),
    current_admin: Users = Depends(get_current_admin_user)
):
    """投稿のステータスを更新"""
    
    success = update_post_status(db, post_id, status)
    if not success:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")
    
    return {"message": "投稿ステータスを更新しました"}

@router.get("/posts/{post_id}", response_model=AdminPostDetailResponse)
def get_post(
    post_id: str,
    db: Session = Depends(get_db),
    # current_admin: Users = Depends(get_current_admin_user)
):
    """投稿詳細を取得"""
    
    post_data = get_post_by_id(db, post_id)

    # メディアアセットの情報からkindが3,4,5のものはpresign_getを呼び出し、urlを取得
    CDN_URL = getenv("CDN_BASE_URL", "")
    for media_asset_id, media_asset_data in post_data['media_assets'].items():
        if media_asset_data['kind'] in [MediaAssetKind.IMAGES, MediaAssetKind.MAIN_VIDEO, MediaAssetKind.SAMPLE_VIDEO]:
            presign_url = presign_get("ingest", media_asset_data['storage_key'])
            post_data['media_assets'][media_asset_id]['storage_key'] = presign_url['download_url']
        elif media_asset_data['kind'] in [MediaAssetKind.OGP, MediaAssetKind.THUMBNAIL]:
            post_data['media_assets'][media_asset_id]['storage_key'] = CDN_URL + "/" + media_asset_data['storage_key']

    if not post_data:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")
    
    return AdminPostDetailResponse(**post_data)


@router.get("/sales", response_model=List[AdminSalesData])
def get_sales_data(
    period: str = Query("monthly", regex="^(daily|weekly|monthly|yearly)$"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: Users = Depends(get_current_admin_user)
):
    """売上データを取得"""
    
    # 仮のデータを返す
    mock_data = [
        {
            "period": "2024-01",
            "total_revenue": 500000,
            "platform_revenue": 50000,
            "creator_revenue": 450000,
            "transaction_count": 100
        },
        {
            "period": "2024-02",
            "total_revenue": 600000,
            "platform_revenue": 60000,
            "creator_revenue": 540000,
            "transaction_count": 120
        }
    ]
    
    return [AdminSalesData(**data) for data in mock_data]

@router.get("/sales/report")
def get_sales_report(
    start_date: str,
    end_date: str,
    format: str = Query("csv", regex="^(csv|json)$"),
    db: Session = Depends(get_db),
    current_admin: Users = Depends(get_current_admin_user)
):
    """売上レポートを出力"""
    
    # 仮のCSVデータ
    csv_data = """期間,総売上,プラットフォーム収益,クリエイター収益,取引件数
2024-01,500000,50000,450000,100
2024-02,600000,60000,540000,120"""
    
    if format == "csv":
        return csv_data
    
    # JSONフォーマットの場合
    return {
        "data": [
            {"period": "2024-01", "total_revenue": 500000, "platform_revenue": 50000, "creator_revenue": 450000, "transaction_count": 100},
            {"period": "2024-02", "total_revenue": 600000, "platform_revenue": 60000, "creator_revenue": 540000, "transaction_count": 120}
        ]
    }
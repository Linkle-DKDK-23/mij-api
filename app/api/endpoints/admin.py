from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

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
    CreateUserRequest
)
from app.models.user import Users
from app.models.creators import Creators
from app.models.identity import IdentityVerifications
from app.models.posts import Posts
from app.models.profiles import Profiles
from app.core.security import hash_password

router = APIRouter()

@router.get("/dashboard/stats", response_model=AdminDashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_admin: Users = Depends(get_current_admin_user)
):
    """管理者ダッシュボード統計情報を取得"""
    
    # 基本統計を手動で計算
    try:
        total_users = db.query(Users).count()
        pending_creator_applications = db.query(Creators).filter(Creators.status == 1).count()
        pending_identity_verifications = db.query(IdentityVerifications).filter(IdentityVerifications.status == 1).count() 
        total_posts = db.query(Posts).count()
    except Exception as e:
        # エラーの場合は仮の値を返す
        total_users = 100
        pending_creator_applications = 5
        pending_identity_verifications = 3
        total_posts = 50
    
    # 今月の売上（仮の値）
    monthly_revenue = 100000
    active_subscriptions = 500
    
    return AdminDashboardStats(
        total_users=total_users,
        pending_creator_applications=pending_creator_applications,
        pending_identity_verifications=pending_identity_verifications,
        total_posts=total_posts,
        monthly_revenue=monthly_revenue,
        active_subscriptions=active_subscriptions
    )

@router.get("/users", response_model=PaginatedResponse[AdminUserResponse])
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    sort: Optional[str] = "created_at_desc",
    db: Session = Depends(get_db),
    current_admin: Users = Depends(get_current_admin_user)
):
    """ユーザー一覧を取得"""
    
    skip = (page - 1) * limit
    
    try:
        query = db.query(Users)
        
        if search:
            query = query.filter(
                (Users.display_name.ilike(f"%{search}%")) |
                (Users.email.ilike(f"%{search}%"))
            )
        
        if role:
            query = query.filter(Users.account_type == role)
        
        # ソート処理
        if sort == "created_at_desc":
            query = query.order_by(Users.created_at.desc())
        elif sort == "created_at_asc":
            query = query.order_by(Users.created_at.asc())
        elif sort == "display_name_asc":
            query = query.order_by(Users.display_name.asc())
        elif sort == "display_name_desc":
            query = query.order_by(Users.display_name.desc())
        elif sort == "email_asc":
            query = query.order_by(Users.email.asc())
        else:
            query = query.order_by(Users.created_at.desc())
        
        total = query.count()
        users = query.offset(skip).limit(limit).all()
        
    except Exception as e:
        # エラーの場合は空のリストを返す
        users = []
        total = 0
    
    return PaginatedResponse(
        data=[AdminUserResponse.from_orm(user) for user in users],
        total=total,
        page=page,
        limit=limit,
        total_pages=(total + limit - 1) // limit if total > 0 else 1
    )

@router.patch("/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    status: str,
    db: Session = Depends(get_db),
    current_admin: Users = Depends(get_current_admin_user)
):
    """ユーザーのステータスを更新"""
    
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    
    # ステータス更新（実装に応じて調整）
    user.account_status = 2 if status == "suspended" else 1
    db.commit()
    db.refresh(user)
    
    return {"message": "ユーザーステータスを更新しました"}

@router.post("/users", response_model=AdminUserResponse)
async def create_user(
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
            slug=user_data.display_name,
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
            display_name=user_data.display_name,
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
async def create_test_admin(
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
            slug="test_admin",
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
            display_name="Test Admin",
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
async def get_creator_applications(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    sort: Optional[str] = "created_at_desc",
    db: Session = Depends(get_db),
    current_admin: Users = Depends(get_current_admin_user)
):
    """クリエイター申請一覧を取得"""
    
    skip = (page - 1) * limit
    
    try:
        query = db.query(Creators).join(Users)
        
        if search:
            query = query.filter(
                (Users.display_name.ilike(f"%{search}%")) |
                (Users.email.ilike(f"%{search}%"))
            )
        
        if status:
            status_map = {"pending": 1, "approved": 2, "rejected": 3}
            query = query.filter(Creators.status == status_map.get(status, 1))
        
        # ソート処理
        if sort == "created_at_desc":
            query = query.order_by(Creators.created_at.desc())
        elif sort == "created_at_asc":
            query = query.order_by(Creators.created_at.asc())
        elif sort == "user_name_asc":
            query = query.order_by(Users.display_name.asc())
        elif sort == "user_name_desc":
            query = query.order_by(Users.display_name.desc())
        else:
            query = query.order_by(Creators.created_at.desc())
        
        total = query.count()
        applications = query.offset(skip).limit(limit).all()
        
    except Exception as e:
        applications = []
        total = 0
    
    return PaginatedResponse(
        data=[AdminCreatorApplicationResponse.from_orm(app) for app in applications],
        total=total,
        page=page,
        limit=limit,
        total_pages=(total + limit - 1) // limit if total > 0 else 1
    )

@router.get("/creator-applications/{application_id}", response_model=AdminCreatorApplicationResponse)
async def get_creator_application(
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
async def review_creator_application(
    application_id: str,
    review: CreatorApplicationReview,
    db: Session = Depends(get_db),
    current_admin: Users = Depends(get_current_admin_user)
):
    """クリエイター申請を審査"""
    
    application = db.query(Creators).filter(Creators.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="申請が見つかりません")
    
    if application.status != 1:  # 1 = pending
        raise HTTPException(status_code=400, detail="この申請は既に審査済みです")
    
    # 申請を更新
    status_map = {"approved": 2, "rejected": 3}  # 2 = approved, 3 = rejected
    application.status = status_map[review.status]
    application.updated_at = datetime.utcnow()
    
    # 承認の場合、ユーザーのアカウントタイプをクリエイターに更新
    if review.status == "approved":
        user = db.query(Users).filter(Users.id == application.user_id).first()
        if user:
            user.account_type = 2  # 2 = creator
    
    db.commit()
    
    return {"message": "申請審査を完了しました"}

@router.get("/identity-verifications", response_model=PaginatedResponse[AdminIdentityVerificationResponse])
async def get_identity_verifications(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    sort: Optional[str] = "created_at_desc",
    db: Session = Depends(get_db),
    current_admin: Users = Depends(get_current_admin_user)
):
    """身分証明審査一覧を取得"""
    
    skip = (page - 1) * limit
    
    try:
        query = db.query(IdentityVerifications).join(Users)
        
        if search:
            query = query.filter(
                (Users.display_name.ilike(f"%{search}%")) |
                (Users.email.ilike(f"%{search}%"))
            )
        
        if status:
            status_map = {"pending": 1, "approved": 2, "rejected": 3}
            query = query.filter(IdentityVerifications.status == status_map.get(status, 1))
        
        # ソート処理
        if sort == "created_at_desc":
            query = query.order_by(IdentityVerifications.created_at.desc())
        elif sort == "created_at_asc":
            query = query.order_by(IdentityVerifications.created_at.asc())
        elif sort == "user_name_asc":
            query = query.order_by(Users.display_name.asc())
        elif sort == "user_name_desc":
            query = query.order_by(Users.display_name.desc())
        else:
            query = query.order_by(IdentityVerifications.created_at.desc())
        
        total = query.count()
        verifications = query.offset(skip).limit(limit).all()
        
    except Exception as e:
        verifications = []
        total = 0
    
    return PaginatedResponse(
        data=[AdminIdentityVerificationResponse.from_orm(v) for v in verifications],
        total=total,
        page=page,
        limit=limit,
        total_pages=(total + limit - 1) // limit if total > 0 else 1
    )

@router.get("/identity-verifications/{verification_id}", response_model=AdminIdentityVerificationResponse)
async def get_identity_verification(
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
async def review_identity_verification(
    verification_id: str,
    review: IdentityVerificationReview,
    db: Session = Depends(get_db),
    current_admin: Users = Depends(get_current_admin_user)
):
    """身分証明を審査"""
    
    verification = db.query(IdentityVerifications).filter(IdentityVerifications.id == verification_id).first()
    if not verification:
        raise HTTPException(status_code=404, detail="審査が見つかりません")
    
    if verification.status != 1:  # 1 = pending
        raise HTTPException(status_code=400, detail="この審査は既に完了済みです")
    
    # 審査を更新
    status_map = {"approved": 2, "rejected": 3}  # 2 = approved, 3 = rejected
    verification.status = status_map[review.status]
    verification.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "身分証明審査を完了しました"}

@router.get("/posts", response_model=PaginatedResponse[AdminPostResponse])
async def get_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    sort: Optional[str] = "created_at_desc",
    db: Session = Depends(get_db),
    current_admin: Users = Depends(get_current_admin_user)
):
    """投稿一覧を取得"""
    
    skip = (page - 1) * limit
    
    try:
        query = db.query(Posts).join(Users)
        
        if search:
            query = query.filter(
                (Posts.title.ilike(f"%{search}%")) |
                (Users.display_name.ilike(f"%{search}%"))
            )
        
        if status:
            status_map = {"draft": 1, "published": 2, "archived": 3}
            query = query.filter(Posts.status == status_map.get(status, 2))
        
        # ソート処理
        if sort == "created_at_desc":
            query = query.order_by(Posts.created_at.desc())
        elif sort == "created_at_asc":
            query = query.order_by(Posts.created_at.asc())
        else:
            query = query.order_by(Posts.created_at.desc())
        
        total = query.count()
        posts = query.offset(skip).limit(limit).all()
        
    except Exception as e:
        posts = []
        total = 0
    
    return PaginatedResponse(
        data=[AdminPostResponse.from_orm(post) for post in posts],
        total=total,
        page=page,
        limit=limit,
        total_pages=(total + limit - 1) // limit if total > 0 else 1
    )

@router.patch("/posts/{post_id}/status")
async def update_post_status(
    post_id: str,
    status: str,
    db: Session = Depends(get_db),
    current_admin: Users = Depends(get_current_admin_user)
):
    """投稿のステータスを更新"""
    
    post = db.query(Posts).filter(Posts.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")
    
    status_map = {"published": 2, "archived": 3, "draft": 1}
    post.status = status_map.get(status, 2)
    post.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "投稿ステータスを更新しました"}

@router.get("/sales", response_model=List[AdminSalesData])
async def get_sales_data(
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
async def get_sales_report(
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
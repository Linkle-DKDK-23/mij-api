from datetime import datetime
from typing import Optional, List, Generic, TypeVar, Dict
from pydantic import BaseModel
from pydantic.generics import GenericModel
import os

CDN_URL = os.getenv("CDN_BASE_URL")

# Generic type for paginated responses
T = TypeVar('T')

class PaginatedResponse(GenericModel, Generic[T]):
    data: List[T]
    total: int
    page: int
    limit: int
    total_pages: int

class AdminDashboardStats(BaseModel):
    total_users: int
    pending_creator_applications: int
    pending_identity_verifications: int
    pending_post_reviews: int  # 投稿申請中件数を追加
    total_posts: int
    monthly_revenue: float
    active_subscriptions: int

class AdminUserResponse(BaseModel):
    id: str
    email: Optional[str]
    role: str  # フロントエンド表示用に文字列として提供
    status: int
    created_at: datetime
    updated_at: datetime
    
    # Profileから取得するフィールド
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, user):
        # roleを数値から文字列に変換
        role_map = {1: "user", 2: "creator", 3: "admin"}
        role_str = role_map.get(user.role, "user")
        
        data = {
            "id": str(user.id),
            "email": user.email,
            "role": role_str,
            "status": user.status,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "display_name": user.profile.display_name if user.profile else None,
            "avatar_url": f"{CDN_URL}/{user.profile.avatar_url}" if user.profile else None
        }
        return cls(**data)

class AdminCreatorApplicationResponse(BaseModel):
    user_id: str
    user: AdminUserResponse
    status: int
    name: Optional[str]
    created_at: datetime
    
    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, creator):
        data = {
            "user_id": str(creator.user_id),
            "user": AdminUserResponse.from_orm(creator.user) if creator.user else None,
            "status": creator.status,
            "name": creator.name,
            "created_at": creator.created_at,
        }
        return cls(**data)

class CreatorApplicationReview(BaseModel):
    status: str  # "approved" or "rejected"
    notes: Optional[str]

class AdminIdentityVerificationResponse(BaseModel):
    id: str
    user_id: str
    user: AdminUserResponse
    status: int
    checked_at: Optional[datetime]
    notes: Optional[str]

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, verification):
        data = {
            "id": str(verification.id),
            "user_id": str(verification.user_id),
            "user": AdminUserResponse.from_orm(verification.user) if verification.user else None,
            "status": verification.status,
            "checked_at": verification.checked_at,
            "notes": verification.notes,
        }
        return cls(**data)

class IdentityVerificationReview(BaseModel):
    status: str  # "approved" or "rejected"
    notes: Optional[str]

class AdminPostResponse(BaseModel):
    id: str
    title: Optional[str]  # フロントエンド側の期待に合わせてtitleフィールドを追加
    content: Optional[str]  # フロントエンド側の期待に合わせてcontentフィールドを追加
    description: Optional[str]
    creator_user_id: str
    creator: AdminUserResponse
    status: str  # フロントエンド側でstring型を期待しているため文字列に変更
    visibility: int
    view_count: int = 0  # フロントエンド側で期待されるフィールドを追加
    like_count: int = 0  # フロントエンド側で期待されるフィールドを追加
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, post):
        # statusを数値から文字列に変換
        status_map = {1: "draft", 2: "published", 3: "archived", 4: "pending", 5: "completed"}
        status_str = status_map.get(post.status, "draft")
        
        data = {
            "id": str(post.id),
            "title": post.description,  # descriptionをtitleとして使用
            "content": post.description,  # descriptionをcontentとして使用
            "description": post.description,
            "creator_user_id": str(post.creator_user_id),
            "creator": AdminUserResponse.from_orm(post.creator) if hasattr(post, 'creator') and post.creator else None,
            "status": status_str,
            "visibility": post.visibility,
            "view_count": getattr(post, 'view_count', 0),
            "like_count": getattr(post, 'like_count', 0),
            "created_at": post.created_at,
            "updated_at": post.updated_at,
        }
        return cls(**data)

class AdminSalesData(BaseModel):
    period: str
    total_revenue: float
    platform_revenue: float
    creator_revenue: float
    transaction_count: int

    class Config:
        orm_mode = True

# Auth schemas for admin
class AdminLoginRequest(BaseModel):
    email: str
    password: str

class AdminLoginResponse(BaseModel):
    token: str
    user: AdminUserResponse

class CreateUserRequest(BaseModel):
    email: str
    password: str
    display_name: str
    role: str

class MediaAssetData(BaseModel):
    kind: int
    storage_key: str

class AdminPostDetailResponse(BaseModel):
    # 投稿情報
    id: str
    description: Optional[str]
    status: int
    created_at: Optional[str]
    post_type: int
    user_id: str
    user_slug: str
    profile_display_name: Optional[str]
    profile_avatar_url: Optional[str]
    media_assets: Dict[str, MediaAssetData]

    class Config:
        orm_mode = True
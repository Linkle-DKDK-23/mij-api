from datetime import datetime
from typing import Optional, List, Generic, TypeVar
from pydantic import BaseModel
from pydantic.generics import GenericModel

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
            "avatar_url": user.profile.avatar_url if user.profile else None
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
    description: Optional[str]
    creator_user_id: str
    creator: AdminUserResponse
    status: int
    visibility: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, post):
        data = {
            "id": str(post.id),
            "description": post.description,
            "creator_user_id": str(post.creator_user_id),
            "creator": AdminUserResponse.from_orm(post.creator) if post.creator else None,
            "status": post.status,
            "visibility": post.visibility,
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
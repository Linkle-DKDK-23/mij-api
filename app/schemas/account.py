from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Dict
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from app.schemas.commons import PresignResponseItem
from app.schemas.purchases import SinglePurchaseResponse
from app.models.posts import Posts

Kind = Literal["avatar", "cover"]

class AccountFileSpec(BaseModel):
    kind: Kind
    content_type: Literal["image/jpeg","image/png","image/webp"]
    ext: Literal["jpg","jpeg","png","webp"]

class LikedPostResponse(BaseModel):
    id: UUID
    description: str
    creator_user_id: UUID
    profile_name: str
    username: str
    avatar_url: Optional[str] = None
    thumbnail_key: Optional[str] = None
    duration_sec: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProfileInfo(BaseModel):
    profile_name: str
    username: str
    avatar_url: Optional[str] = None
    cover_url: Optional[str] = None

class SocialInfo(BaseModel):
    followers_count: int
    following_count: int
    total_likes: int
    liked_posts: List[LikedPostResponse] = []

class PostsInfo(BaseModel):
    pending_posts_count: int
    rejected_posts_count: int
    unpublished_posts_count: int
    deleted_posts_count: int
    approved_posts_count: int

class SalesInfo(BaseModel):
    total_sales: int

class PlanInfo(BaseModel):
    plan_count: int
    total_price: int
    subscribed_plan_count: int
    subscribed_total_price: int
    subscribed_plan_details: List[dict] = []
    single_purchases_count: int
    single_purchases_data: List[SinglePurchaseResponse] = []

class PlansSubscribedInfo(BaseModel):
    plan_count: int
    total_price: int
    subscribed_plan_count: int
    subscribed_total_price: int
    subscribed_plan_names: List[str] = []
    subscribed_plan_details: List[dict] = []

class AccountInfoResponse(BaseModel):
    profile_info: ProfileInfo
    social_info: SocialInfo
    posts_info: PostsInfo
    sales_info: SalesInfo
    plan_info: PlanInfo

class AvatarPresignRequest(BaseModel):
    files: List[AccountFileSpec] = Field(..., description='例: [{"kind":"avatar","ext":"jpg"}, ...]')

class AccountPresignResponse(BaseModel):
    uploads: dict[str, PresignResponseItem]

class AccountUpdateRequest(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    description: Optional[str] = None
    links: Optional[dict] = None
    avatar_url: Optional[str] = None
    cover_url: Optional[str] = None

class AccountUpdateResponse(BaseModel):
    message: str
    success: bool

class AccountPostResponse(BaseModel):
    id: str
    description: str
    thumbnail_url: Optional[str] = None
    likes_count: int
    creator_name: str
    username: str
    creator_avatar_url: Optional[str] = None
    price: int
    currency: str

class AccountPostStatusResponse(BaseModel):
    pending_posts: List[AccountPostResponse] = []
    rejected_posts: List[AccountPostResponse] = []
    unpublished_posts: List[AccountPostResponse] = []
    deleted_posts: List[AccountPostResponse] = []
    approved_posts: List[AccountPostResponse] = []
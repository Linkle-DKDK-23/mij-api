from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Dict
from app.schemas.commons import PresignResponseItem
from app.models.posts import Posts

Kind = Literal["avatar", "cover"]

class AccountFileSpec(BaseModel):
    kind: Kind
    content_type: Literal["image/jpeg","image/png","image/webp"]
    ext: Literal["jpg","jpeg","png","webp"]

class AccountInfoResponse(BaseModel):
    slug: str
    display_name: str
    avatar_url: Optional[str] = None
    cover_url: Optional[str] = None
    followers_count: int
    following_count: int
    total_likes: int
    pending_posts_count: int
    rejected_posts_count: int
    unpublished_posts_count: int
    deleted_posts_count: int
    approved_posts_count: int
    total_sales: int
    plan_count: int
    total_plan_price: int

class AvatarPresignRequest(BaseModel):
    files: List[AccountFileSpec] = Field(..., description='例: [{"kind":"avatar","ext":"jpg"}, ...]')

class AccountPresignResponse(BaseModel):
    uploads: dict[str, PresignResponseItem]

class AccountUpdateRequest(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
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
    display_name: str
    creator_avatar_url: Optional[str] = None
    price: int
    currency: str

class AccountPostStatusResponse(BaseModel):
    pending_posts: List[AccountPostResponse] = []
    rejected_posts: List[AccountPostResponse] = []
    unpublished_posts: List[AccountPostResponse] = []
    deleted_posts: List[AccountPostResponse] = []
    approved_posts: List[AccountPostResponse] = []
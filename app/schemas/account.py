from pydantic import BaseModel
from typing import Optional

class AccountInfoResponse(BaseModel):
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

class AccountUpdateRequest(BaseModel):
    name: Optional[str] = None  # users.slug
    display_name: Optional[str] = None  # profiles.display_name

class AccountUpdateResponse(BaseModel):
    message: str
    success: bool

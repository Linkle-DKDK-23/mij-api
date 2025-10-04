from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime

class PurchaseCreateRequest(BaseModel):
    post_id: UUID
    plan_id: UUID

class SinglePurchaseResponse(BaseModel):
    purchase_id: UUID
    post_id: UUID
    plan_id: UUID
    post_title: str
    post_description: str
    creator_name: str
    creator_username: str
    creator_avatar_url: Optional[str] = None
    thumbnail_key: Optional[str] = None
    purchase_price: int
    purchase_created_at: datetime
    
    class Config:
        from_attributes = True

class SinglePurchaseListResponse(BaseModel):
    single_purchases: list[SinglePurchaseResponse]
    total_count: int
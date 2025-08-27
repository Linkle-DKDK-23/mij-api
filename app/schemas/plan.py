from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, List
from datetime import datetime

class PlanCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: int = Field(..., gt=0)
    currency: str = Field(default="JPY")
    billing_cycle: int = Field(default=1)

class PlanResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    price: int
    
    class Config:
        from_attributes = True

class PlanListResponse(BaseModel):
    plans: List[PlanResponse]

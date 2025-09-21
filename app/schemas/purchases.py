from pydantic import BaseModel
from uuid import UUID

class PurchaseCreateRequest(BaseModel):
    post_id: UUID
    plan_id: UUID
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, List
from datetime import datetime

class PostCreateRequest(BaseModel):
	description: str
	category_ids: List[str]
	tags: Optional[str] = None
	scheduled: bool
	formattedScheduledDateTime: Optional[str] = None
	expiration: bool
	expirationDate: Optional[datetime] = None
	plan: bool
	plan_ids: Optional[List[UUID]] = None
	single: bool
	price: Optional[int] = None


class PostResponse(BaseModel):
	id: UUID
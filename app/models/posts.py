from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from uuid import UUID
from datetime import datetime

from sqlalchemy import ForeignKey, Text, SmallInteger, BigInteger, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.base import Base

if TYPE_CHECKING:
    from .user import Users
    from .post_categories import PostCategories
    from .media_assets import MediaAssets
    from .post_moderation_events import PostModerationEvents
    from .plans import PostPlans
    from .purchases import Purchases

class Posts(Base):
    __tablename__ = "posts"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    creator_user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=False)
    thumbnail_storage_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    video_storage_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    video_duration: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    visibility: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    status: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    expiration_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    moderation_state: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    moderation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    moderation_flags: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    moderated_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    moderated_by: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    creator: Mapped["Users"] = relationship("Users", back_populates="posts")
    post_categories: Mapped[List["PostCategories"]] = relationship("PostCategories", back_populates="post")
    media_assets: Mapped[List["MediaAssets"]] = relationship("MediaAssets", back_populates="post")
    moderation_events: Mapped[List["PostModerationEvents"]] = relationship("PostModerationEvents", back_populates="post")
    post_plans: Mapped[List["PostPlans"]] = relationship("PostPlans", back_populates="post")
    pure_purchases: Mapped[List["Purchases"]] = relationship("Purchases", back_populates="post")

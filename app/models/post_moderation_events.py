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
    from .posts import Posts

class PostModerationEvents(Base):
    __tablename__ = "post_moderation_events"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    post_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)

    to_state: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    flags: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    acted_by_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    acted_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    post: Mapped["Posts"] = relationship("Posts", back_populates="moderation_events")
    acted_by: Mapped["Users"] = relationship("Users", back_populates="moderation_events",foreign_keys=[acted_by_id])
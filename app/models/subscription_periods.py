from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from datetime import datetime

from sqlalchemy import ForeignKey, Text, SmallInteger, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.base import Base

if TYPE_CHECKING:
    from .subscriptions import Subscriptions

class SubscriptionPeriods(Base):
    __tablename__ = "subscription_periods"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    subscription_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False)
    period_start: Mapped[datetime] = mapped_column(nullable=False)
    period_end: Mapped[datetime] = mapped_column(nullable=False)
    status: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    invoice_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from datetime import datetime

from sqlalchemy import ForeignKey, Text, BigInteger, SmallInteger, func, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.base import Base

if TYPE_CHECKING:
    from .plans import Plans

class Prices(Base):
    __tablename__ = "prices"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    plan_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    interval: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    currency: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    unit_amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    external_price_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    plan: Mapped["Plans"] = relationship("Plans", back_populates="prices")

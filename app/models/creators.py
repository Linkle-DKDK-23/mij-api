from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from datetime import datetime

from sqlalchemy import ForeignKey, Text, SmallInteger, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, CITEXT, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.base import Base

if TYPE_CHECKING:
    from .user import Users
    from .categories import Categories

class Creators(Base):
    __tablename__ = "creators"

    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    first_name_kana: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_name_kana: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    birth_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    status: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    category_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    country_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tax_info: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    tos_accepted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    user: Mapped["Users"] = relationship("Users", back_populates="creator")
    category: Mapped[Optional["Categories"]] = relationship("Categories", back_populates="creators")

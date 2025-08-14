from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from datetime import datetime

from sqlalchemy import ForeignKey, Text, SmallInteger, BigInteger, func, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.base import Base

if TYPE_CHECKING:
    from .user import Users
    from .orders import OrderItems

class PayoutAccounts(Base):
    __tablename__ = "payout_accounts"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    creator_user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    provider: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    external_account_id: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)

    creator: Mapped["Users"] = relationship("Users")

class Payouts(Base):
    __tablename__ = "payouts"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    creator_user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    status: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    paid_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    creator: Mapped["Users"] = relationship("Users")
    items: Mapped[list["PayoutItems"]] = relationship("PayoutItems", back_populates="payout")

class PayoutItems(Base):
    __tablename__ = "payout_items"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    payout_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("payouts.id", ondelete="CASCADE"), nullable=False)
    order_item_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("order_items.id"), nullable=False)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)

    payout: Mapped["Payouts"] = relationship("Payouts", back_populates="items")
    order_item: Mapped["OrderItems"] = relationship("OrderItems")

class CreatorBalances(Base):
    __tablename__ = "creator_balances"

    creator_user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    available: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    pending: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    currency: Mapped[str] = mapped_column(CHAR(3), nullable=False, default="JPY")

    creator: Mapped["Users"] = relationship("Users")

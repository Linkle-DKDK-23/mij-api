from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from uuid import uuid4, UUID
from datetime import datetime

from sqlalchemy import ForeignKey, Text, SmallInteger, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, CITEXT
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.base import Base

if TYPE_CHECKING:
    from .profiles import Profiles
    from .creators import Creators
    from .posts import Posts
    from .plans import Plans
    from .subscriptions import Subscriptions
    from .orders import Orders

class Users(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    email: Mapped[Optional[str]] = mapped_column(CITEXT, unique=True, nullable=True)
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    password_hash: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    role: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    status: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    
    profile: Mapped[Optional["Profiles"]] = relationship("Profiles", back_populates="user", uselist=False)
    creator: Mapped[Optional["Creators"]] = relationship("Creators", back_populates="user", uselist=False)
    posts: Mapped[List["Posts"]] = relationship("Posts", back_populates="creator")
    plans: Mapped[List["Plans"]] = relationship("Plans", back_populates="creator")
    subscriptions: Mapped[List["Subscriptions"]] = relationship("Subscriptions", back_populates="user")
    orders: Mapped[List["Orders"]] = relationship("Orders", back_populates="user")
    
     
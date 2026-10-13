from __future__ import annotations

from datetime import datetime
from typing import TypeAlias

from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, Index, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.base import Base

JsonScalar: TypeAlias = str | int | float | bool | None


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    display_name: Mapped[str | None] = mapped_column(String(120))
    auth_provider: Mapped[str | None] = mapped_column(String(40))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    preferences: Mapped[list[UserPreference]] = relationship(back_populates="user")
    saved_schools: Mapped[list[SavedSchool]] = relationship(back_populates="user")


class UserPreference(Base):
    __tablename__ = "user_preferences"
    __table_args__ = (
        Index("ix_user_preferences_user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    intended_major: Mapped[str | None] = mapped_column(String(120))
    home_state: Mapped[str | None] = mapped_column(String(2))
    max_annual_cost: Mapped[int | None] = mapped_column(Integer)
    weights: Mapped[dict[str, JsonScalar]] = mapped_column(JSON, default=dict)
    constraints: Mapped[dict[str, JsonScalar]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped[User] = relationship(back_populates="preferences")


class SavedSchool(Base):
    __tablename__ = "saved_schools"
    __table_args__ = (
        Index("ix_saved_schools_user_id", "user_id"),
        Index("ix_saved_schools_school_id", "school_id"),
        UniqueConstraint("user_id", "school_id", name="uq_saved_schools_user_school"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped[User] = relationship(back_populates="saved_schools")

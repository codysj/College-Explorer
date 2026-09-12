from __future__ import annotations

from datetime import datetime
from typing import TypeAlias

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from db.base import Base

JsonScalar: TypeAlias = str | int | float | bool | None


class AcceptanceOffer(Base):
    __tablename__ = "acceptance_offers"
    __table_args__ = (UniqueConstraint("user_id", "school_id", name="uq_acceptance_offers_user_school"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    aid_offer: Mapped[int | None] = mapped_column(Integer)
    scholarships: Mapped[int | None] = mapped_column(Integer)
    estimated_yearly_cost: Mapped[int | None] = mapped_column(Integer)
    visit_notes: Mapped[str | None] = mapped_column(Text)
    unresolved_concerns: Mapped[list[str]] = mapped_column(JSON, default=list)
    parent_priority_notes: Mapped[str | None] = mapped_column(Text)
    student_priority_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DecisionSummarySnapshot(Base):
    __tablename__ = "decision_summary_snapshots"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    summary_version: Mapped[str] = mapped_column(String(24), nullable=False)
    school_ids: Mapped[list[int]] = mapped_column(JSON, default=list)
    summary: Mapped[dict[str, JsonScalar | list[JsonScalar] | dict[str, JsonScalar]]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

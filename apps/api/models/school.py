from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Numeric, SmallInteger, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.base import Base


class School(Base):
    __tablename__ = "schools"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    unitid: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    city: Mapped[str] = mapped_column(String(80), nullable=False)
    state: Mapped[str] = mapped_column(String(2), nullable=False)
    region: Mapped[str] = mapped_column(String(32), nullable=False)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    setting: Mapped[str] = mapped_column(String(32), nullable=False)
    undergraduate_enrollment: Mapped[int | None] = mapped_column(Integer)
    acceptance_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    source_name: Mapped[str] = mapped_column(String(80), nullable=False)
    source_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    data_version: Mapped[str] = mapped_column(String(40), nullable=False)
    imported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    refreshed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    academics: Mapped[SchoolAcademics | None] = relationship(back_populates="school")
    costs: Mapped[SchoolCosts | None] = relationship(back_populates="school")
    outcomes: Mapped[SchoolOutcomes | None] = relationship(back_populates="school")
    campus_life: Mapped[SchoolCampusLife | None] = relationship(back_populates="school")


class SchoolAcademics(Base):
    __tablename__ = "school_academics"

    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), primary_key=True)
    top_majors: Mapped[list[str]] = mapped_column(ARRAY(String(80)), default=list)
    graduation_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    retention_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    student_faculty_ratio: Mapped[Decimal | None] = mapped_column(Numeric(4, 1))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    school: Mapped[School] = relationship(back_populates="academics")


class SchoolCosts(Base):
    __tablename__ = "school_costs"

    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), primary_key=True)
    tuition_in_state: Mapped[int | None] = mapped_column(Integer)
    tuition_out_state: Mapped[int | None] = mapped_column(Integer)
    net_price: Mapped[int | None] = mapped_column(Integer)
    average_aid: Mapped[int | None] = mapped_column(Integer)
    debt_median: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    school: Mapped[School] = relationship(back_populates="costs")


class SchoolOutcomes(Base):
    __tablename__ = "school_outcomes"

    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), primary_key=True)
    median_earnings: Mapped[int | None] = mapped_column(Integer)
    repayment_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    school: Mapped[School] = relationship(back_populates="outcomes")


class SchoolCampusLife(Base):
    __tablename__ = "school_campus_life"

    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id", ondelete="CASCADE"), primary_key=True)
    housing_available: Mapped[bool | None]
    sports_division: Mapped[str | None] = mapped_column(String(16))
    greek_life_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    culture_tags: Mapped[list[str]] = mapped_column(ARRAY(String(80)), default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    school: Mapped[School] = relationship(back_populates="campus_life")

"""initial schema

Revision ID: 20260509_0001
Revises:
Create Date: 2026-05-09 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260509_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "schools",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("unitid", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("city", sa.String(length=80), nullable=False),
        sa.Column("state", sa.String(length=2), nullable=False),
        sa.Column("region", sa.String(length=32), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("setting", sa.String(length=32), nullable=False),
        sa.Column("undergraduate_enrollment", sa.Integer(), nullable=True),
        sa.Column("acceptance_rate", sa.Numeric(5, 4), nullable=True),
        sa.Column("latitude", sa.Numeric(9, 6), nullable=True),
        sa.Column("longitude", sa.Numeric(9, 6), nullable=True),
        sa.Column("source_name", sa.String(length=80), nullable=False),
        sa.Column("source_year", sa.SmallInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("undergraduate_enrollment IS NULL OR undergraduate_enrollment >= 0", name="ck_schools_enrollment_nonnegative"),
        sa.CheckConstraint("acceptance_rate IS NULL OR (acceptance_rate >= 0 AND acceptance_rate <= 1)", name="ck_schools_acceptance_rate_range"),
        sa.UniqueConstraint("unitid", name="uq_schools_unitid"),
    )
    op.create_index("ix_schools_state", "schools", ["state"])
    op.create_index("ix_schools_region", "schools", ["region"])
    op.create_index("ix_schools_type", "schools", ["type"])
    op.create_index("ix_schools_setting", "schools", ["setting"])
    op.create_index("ix_schools_enrollment", "schools", ["undergraduate_enrollment"])
    op.create_index("ix_schools_acceptance_rate", "schools", ["acceptance_rate"])

    op.create_table(
        "school_academics",
        sa.Column("school_id", sa.BigInteger(), sa.ForeignKey("schools.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("top_majors", sa.ARRAY(sa.String(length=80)), nullable=False, server_default=sa.text("'{}'::varchar[]")),
        sa.Column("graduation_rate", sa.Numeric(5, 4), nullable=True),
        sa.Column("retention_rate", sa.Numeric(5, 4), nullable=True),
        sa.Column("student_faculty_ratio", sa.Numeric(4, 1), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("graduation_rate IS NULL OR (graduation_rate >= 0 AND graduation_rate <= 1)", name="ck_academics_graduation_rate_range"),
        sa.CheckConstraint("retention_rate IS NULL OR (retention_rate >= 0 AND retention_rate <= 1)", name="ck_academics_retention_rate_range"),
        sa.CheckConstraint("student_faculty_ratio IS NULL OR student_faculty_ratio > 0", name="ck_academics_student_faculty_positive"),
    )
    op.create_index("ix_school_academics_graduation_rate", "school_academics", ["graduation_rate"])

    op.create_table(
        "school_costs",
        sa.Column("school_id", sa.BigInteger(), sa.ForeignKey("schools.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tuition_in_state", sa.Integer(), nullable=True),
        sa.Column("tuition_out_state", sa.Integer(), nullable=True),
        sa.Column("net_price", sa.Integer(), nullable=True),
        sa.Column("average_aid", sa.Integer(), nullable=True),
        sa.Column("debt_median", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("tuition_in_state IS NULL OR tuition_in_state >= 0", name="ck_costs_tuition_in_state_nonnegative"),
        sa.CheckConstraint("tuition_out_state IS NULL OR tuition_out_state >= 0", name="ck_costs_tuition_out_state_nonnegative"),
        sa.CheckConstraint("net_price IS NULL OR net_price >= 0", name="ck_costs_net_price_nonnegative"),
        sa.CheckConstraint("average_aid IS NULL OR average_aid >= 0", name="ck_costs_average_aid_nonnegative"),
        sa.CheckConstraint("debt_median IS NULL OR debt_median >= 0", name="ck_costs_debt_median_nonnegative"),
    )
    op.create_index("ix_school_costs_tuition_in_state", "school_costs", ["tuition_in_state"])
    op.create_index("ix_school_costs_tuition_out_state", "school_costs", ["tuition_out_state"])
    op.create_index("ix_school_costs_net_price", "school_costs", ["net_price"])

    op.create_table(
        "school_outcomes",
        sa.Column("school_id", sa.BigInteger(), sa.ForeignKey("schools.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("median_earnings", sa.Integer(), nullable=True),
        sa.Column("repayment_rate", sa.Numeric(5, 4), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("median_earnings IS NULL OR median_earnings >= 0", name="ck_outcomes_median_earnings_nonnegative"),
        sa.CheckConstraint("repayment_rate IS NULL OR (repayment_rate >= 0 AND repayment_rate <= 1)", name="ck_outcomes_repayment_rate_range"),
    )

    op.create_table(
        "school_campus_life",
        sa.Column("school_id", sa.BigInteger(), sa.ForeignKey("schools.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("housing_available", sa.Boolean(), nullable=True),
        sa.Column("sports_division", sa.String(length=16), nullable=True),
        sa.Column("greek_life_rate", sa.Numeric(5, 4), nullable=True),
        sa.Column("culture_tags", sa.ARRAY(sa.String(length=80)), nullable=False, server_default=sa.text("'{}'::varchar[]")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("greek_life_rate IS NULL OR (greek_life_rate >= 0 AND greek_life_rate <= 1)", name="ck_campus_greek_life_rate_range"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("display_name", sa.String(length=120), nullable=True),
        sa.Column("auth_provider", sa.String(length=40), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )

    op.create_table(
        "user_preferences",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("intended_major", sa.String(length=120), nullable=True),
        sa.Column("home_state", sa.String(length=2), nullable=True),
        sa.Column("max_annual_cost", sa.Integer(), nullable=True),
        sa.Column("weights", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("constraints", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("max_annual_cost IS NULL OR max_annual_cost >= 0", name="ck_preferences_max_cost_nonnegative"),
    )
    op.create_index("ix_user_preferences_user_id", "user_preferences", ["user_id"])

    op.create_table(
        "saved_schools",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("school_id", sa.BigInteger(), sa.ForeignKey("schools.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("status IN ('interested', 'applying', 'accepted', 'finalist', 'removed')", name="ck_saved_schools_status"),
        sa.UniqueConstraint("user_id", "school_id", name="uq_saved_schools_user_school"),
    )
    op.create_index("ix_saved_schools_user_id", "saved_schools", ["user_id"])
    op.create_index("ix_saved_schools_school_id", "saved_schools", ["school_id"])

    op.create_table(
        "comparisons",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_comparisons_user_id", "comparisons", ["user_id"])

    op.create_table(
        "comparison_schools",
        sa.Column("comparison_id", sa.BigInteger(), sa.ForeignKey("comparisons.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("school_id", sa.BigInteger(), sa.ForeignKey("schools.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("position", sa.SmallInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("position >= 1 AND position <= 5", name="ck_comparison_schools_position_range"),
        sa.UniqueConstraint("comparison_id", "position", name="uq_comparison_schools_position"),
    )
    op.create_index("ix_comparison_schools_school_id", "comparison_schools", ["school_id"])

    op.create_table(
        "events",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("event_name", sa.String(length=80), nullable=False),
        sa.Column("entity_type", sa.String(length=40), nullable=True),
        sa.Column("entity_id", sa.BigInteger(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_events_user_id", "events", ["user_id"])
    op.create_index("ix_events_event_name", "events", ["event_name"])
    op.create_index("ix_events_created_at", "events", ["created_at"])


def downgrade() -> None:
    op.drop_table("events")
    op.drop_table("comparison_schools")
    op.drop_table("comparisons")
    op.drop_table("saved_schools")
    op.drop_table("user_preferences")
    op.drop_table("users")
    op.drop_table("school_campus_life")
    op.drop_table("school_outcomes")
    op.drop_table("school_costs")
    op.drop_table("school_academics")
    op.drop_table("schools")

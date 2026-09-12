"""acceptance decision mode

Revision ID: 20260521_0004
Revises: 20260521_0003
Create Date: 2026-05-21 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260521_0004"
down_revision: Union[str, None] = "20260521_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "acceptance_offers",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("school_id", sa.BigInteger(), sa.ForeignKey("schools.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("aid_offer", sa.Integer(), nullable=True),
        sa.Column("scholarships", sa.Integer(), nullable=True),
        sa.Column("estimated_yearly_cost", sa.Integer(), nullable=True),
        sa.Column("visit_notes", sa.Text(), nullable=True),
        sa.Column("unresolved_concerns", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("parent_priority_notes", sa.Text(), nullable=True),
        sa.Column("student_priority_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("status IN ('accepted', 'finalist')", name="ck_acceptance_offers_status"),
        sa.CheckConstraint("aid_offer IS NULL OR aid_offer >= 0", name="ck_acceptance_offers_aid_nonnegative"),
        sa.CheckConstraint("scholarships IS NULL OR scholarships >= 0", name="ck_acceptance_offers_scholarships_nonnegative"),
        sa.CheckConstraint("estimated_yearly_cost IS NULL OR estimated_yearly_cost >= 0", name="ck_acceptance_offers_cost_nonnegative"),
        sa.UniqueConstraint("user_id", "school_id", name="uq_acceptance_offers_user_school"),
    )
    op.create_index("ix_acceptance_offers_user_id", "acceptance_offers", ["user_id"])
    op.create_index("ix_acceptance_offers_school_id", "acceptance_offers", ["school_id"])

    op.create_table(
        "decision_summary_snapshots",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("summary_version", sa.String(length=24), nullable=False),
        sa.Column("school_ids", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("summary", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_decision_summary_snapshots_user_id", "decision_summary_snapshots", ["user_id"])


def downgrade() -> None:
    op.drop_table("decision_summary_snapshots")
    op.drop_table("acceptance_offers")

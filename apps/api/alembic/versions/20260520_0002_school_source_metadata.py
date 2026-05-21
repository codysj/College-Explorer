"""add school source metadata

Revision ID: 20260520_0002
Revises: 20260509_0001
Create Date: 2026-05-20 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260520_0002"
down_revision: Union[str, None] = "20260509_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("schools", sa.Column("data_version", sa.String(length=40), nullable=False, server_default="v1_seed"))
    op.add_column("schools", sa.Column("imported_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("schools", sa.Column("refreshed_at", sa.DateTime(timezone=True), nullable=True))
    op.alter_column("schools", "data_version", server_default=None)


def downgrade() -> None:
    op.drop_column("schools", "refreshed_at")
    op.drop_column("schools", "imported_at")
    op.drop_column("schools", "data_version")


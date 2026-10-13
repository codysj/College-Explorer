"""add school_academics.majors_offered

top_majors holds a school's three largest program families, so ranking could not tell a
program that is not offered from one that is merely smaller than the top three. This
column holds every family with graduates.

Revision ID: 20261013_0006
Revises: 20261013_0005
Create Date: 2026-10-13 00:00:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261013_0006"
down_revision: Union[str, None] = "20261013_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "school_academics",
        sa.Column("majors_offered", sa.ARRAY(sa.String(length=80)), nullable=False, server_default=sa.text("'{}'::varchar[]")),
    )


def downgrade() -> None:
    op.drop_column("school_academics", "majors_offered")

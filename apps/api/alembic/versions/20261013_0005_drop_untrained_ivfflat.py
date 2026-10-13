"""drop the IVFFlat index on school_embeddings

The index was created on an empty table, so its 16 list centroids were trained on no data.
At the current 92 schools the planner ignores it and scans exactly. On a larger corpus it
would start being used, and with the default ivfflat.probes = 1 over untrained centroids it
would silently return wrong neighbours. An exact scan is correct and fast at this size;
recreate the index after loading data (lists ~ rows / 1000) if the corpus grows past a few
thousand schools.

Revision ID: 20261013_0005
Revises: 20260521_0004
Create Date: 2026-10-13 00:00:00
"""

from typing import Sequence, Union

from alembic import op

revision: str = "20261013_0005"
down_revision: Union[str, None] = "20260521_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_school_embeddings_vector_cosine", table_name="school_embeddings")


def downgrade() -> None:
    op.execute(
        """
        CREATE INDEX ix_school_embeddings_vector_cosine
        ON school_embeddings
        USING ivfflat (vector vector_cosine_ops)
        WITH (lists = 16)
        """
    )

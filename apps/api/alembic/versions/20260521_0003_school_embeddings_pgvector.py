"""add pgvector school embeddings

Revision ID: 20260521_0003
Revises: 20260520_0002
Create Date: 2026-05-21 00:00:00
"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260521_0003"
down_revision: Union[str, None] = "20260520_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute(
        """
        CREATE TABLE school_embeddings (
            school_id bigint NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
            embedding_type varchar(40) NOT NULL,
            embedding_model varchar(80) NOT NULL,
            vector vector(64) NOT NULL,
            text_snapshot_hash varchar(64) NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now(),
            refreshed_at timestamptz NOT NULL DEFAULT now(),
            PRIMARY KEY (school_id, embedding_type, embedding_model)
        )
        """
    )
    op.create_index("ix_school_embeddings_type_model", "school_embeddings", ["embedding_type", "embedding_model"])
    op.execute(
        """
        CREATE INDEX ix_school_embeddings_vector_cosine
        ON school_embeddings
        USING ivfflat (vector vector_cosine_ops)
        WITH (lists = 16)
        """
    )


def downgrade() -> None:
    op.drop_index("ix_school_embeddings_vector_cosine", table_name="school_embeddings")
    op.drop_index("ix_school_embeddings_type_model", table_name="school_embeddings")
    op.drop_table("school_embeddings")

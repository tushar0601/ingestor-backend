"""create_file_object_table

Revision ID: 0fb0f0373300
Revises: f3cac7af148f
Create Date: 2025-12-16 03:06:53.451830
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0fb0f0373300"
down_revision: Union[str, None] = "f3cac7af148f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # UUID generation on DB side (recommended)
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    op.create_table(
        "file_object",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("storage_path", sa.String(length=1024), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("upload_mode", sa.String(length=16), nullable=False),
        sa.Column("file_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenant.tenant_object.id"],
            name="fk_file_object_tenant_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_file_object"),
        schema="file",
    )

    # Indexes (match your model intent; include schema)
    op.create_index(
        "ix_file_file_object_tenant_id",
        "file_object",
        ["tenant_id"],
        unique=False,
        schema="file",
    )
    op.create_index(
        "ix_file_file_object_original_filename",
        "file_object",
        ["original_filename"],
        unique=False,
        schema="file",
    )
    op.create_index(
        "ix_file_file_object_content_type",
        "file_object",
        ["content_type"],
        unique=False,
        schema="file",
    )
    op.create_index(
        "ix_file_file_object_status",
        "file_object",
        ["status"],
        unique=False,
        schema="file",
    )
    op.create_index(
        "ix_file_file_object_upload_mode",
        "file_object",
        ["upload_mode"],
        unique=False,
        schema="file",
    )


def downgrade() -> None:
    op.drop_index("ix_file_file_object_upload_mode", table_name="file_object", schema="file")
    op.drop_index("ix_file_file_object_status", table_name="file_object", schema="file")
    op.drop_index("ix_file_file_object_content_type", table_name="file_object", schema="file")
    op.drop_index("ix_file_file_object_original_filename", table_name="file_object", schema="file")
    op.drop_index("ix_file_file_object_tenant_id", table_name="file_object", schema="file")
    op.drop_table("file_object", schema="file")

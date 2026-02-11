"""create upload_sessions table

Revision ID: 08590cabd180
Revises: 20c598a2b66d
Create Date: 2026-02-06 01:32:56.081044

"""

from typing import Sequence, Union
from sqlalchemy.dialects import postgresql

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "08590cabd180"
down_revision: Union[str, None] = "20c598a2b66d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "upload_sessions",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("content_type", sa.String(), nullable=True),
        sa.Column("size_bytes_expected", sa.BigInteger(), nullable=False),
        sa.Column("bucket", sa.String(), nullable=False),
        sa.Column("object_key", sa.String(), nullable=False),
        sa.Column("storage_upload_id", sa.String(), nullable=False),
        sa.Column("part_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("processing_job_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("error_code", sa.String(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("idempotency_key", sa.String(), nullable=True),
        schema="jobs",
    )

    op.create_index(
        "ix_upload_sessions_tenant_id_created_at",
        "upload_sessions",
        ["tenant_id", "created_at"],
        schema="jobs",
    )

    op.create_index(
        "ix_upload_sessions_status_expires_at",
        "upload_sessions",
        ["status", "expires_at"],
        schema="jobs",
    )

    op.create_index(
        "ix_upload_sessions_tenant_idempotency_key",
        "upload_sessions",
        ["tenant_id", "idempotency_key"],
        unique=True,
        schema="jobs",
    )

    op.create_index(
        "ix_upload_sessions_bucket_object_key",
        "upload_sessions",
        ["bucket", "object_key"],
        unique=True,
        schema="jobs",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_upload_sessions_bucket_object_key",
        table_name="upload_sessions",
        schema="jobs",
    )
    op.drop_index(
        "ix_upload_sessions_tenant_idempotency_key",
        table_name="upload_sessions",
        schema="jobs",
    )
    op.drop_index(
        "ix_upload_sessions_status_expires_at",
        table_name="upload_sessions",
        schema="jobs",
    )
    op.drop_index(
        "ix_upload_sessions_tenant_id_created_at",
        table_name="upload_sessions",
        schema="jobs",
    )

    op.drop_table("upload_sessions", schema="jobs")

"""adjust jobs.job_object schema/indexes/etc

Revision ID: 3184c0364491
Revises: 22b5391efdf4
Create Date: 2026-01-16 18:00:28.065622

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "3184c0364491"
down_revision: Union[str, None] = "22b5391efdf4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    op.create_table(
        "job_object",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("error_message", sa.String(length=2000), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenant.tenant_object.id"],
            name="fk_job_object_tenant_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["file_id"],
            ["file.file_object.id"],
            name="fk_job_object_file_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_job_object"),
        schema="jobs",
    )

    # Indexes (matching model intent; include schema)
    op.create_index(
        "ix_jobs_job_object_tenant_id",
        "job_object",
        ["tenant_id"],
        unique=False,
        schema="jobs",
    )
    op.create_index(
        "ix_jobs_job_object_file_id",
        "job_object",
        ["file_id"],
        unique=False,
        schema="jobs",
    )
    op.create_index(
        "ix_jobs_job_object_job_type",
        "job_object",
        ["job_type"],
        unique=False,
        schema="jobs",
    )
    op.create_index(
        "ix_jobs_job_object_status",
        "job_object",
        ["status"],
        unique=False,
        schema="jobs",
    )


def downgrade() -> None:
    op.drop_index("ix_jobs_job_object_status", table_name="job_object", schema="jobs")
    op.drop_index("ix_jobs_job_object_job_type", table_name="job_object", schema="jobs")
    op.drop_index("ix_jobs_job_object_file_id", table_name="job_object", schema="jobs")
    op.drop_index(
        "ix_jobs_job_object_tenant_id", table_name="job_object", schema="jobs"
    )
    op.drop_table("job_object", schema="jobs")

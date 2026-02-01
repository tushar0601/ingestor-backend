"""add retry and backoff fields to jobs

Revision ID: 20c598a2b66d
Revises: 3184c0364491
Create Date: 2026-01-23 16:51:54.199649

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '20c598a2b66d'
down_revision: Union[str, None] = '3184c0364491'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("job_object", sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"), schema="jobs")
    op.add_column("job_object", sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="5"), schema="jobs")
    op.add_column(
        "job_object",
        sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="jobs",
    )
    op.add_column("job_object", sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True), schema="jobs")
    op.add_column("job_object", sa.Column("last_error", sa.Text(), nullable=True), schema="jobs")

    op.create_index(
        "ix_jobs_job_object_status_next_run_at",
        "job_object",
        ["status", "next_run_at"],
        unique=False,
        schema="jobs",
    )

    op.create_index(
        "ix_jobs_job_object_locked_at",
        "job_object",
        ["locked_at"],
        unique=False,
        schema="jobs",
    )


def downgrade() -> None:
    op.drop_index("ix_jobs_job_object_locked_at", table_name="job_object", schema="jobs")
    op.drop_index("ix_jobs_job_object_status_next_run_at", table_name="job_object", schema="jobs")

    op.drop_column("job_object", "last_error", schema="jobs")
    op.drop_column("job_object", "locked_at", schema="jobs")
    op.drop_column("job_object", "next_run_at", schema="jobs")
    op.drop_column("job_object", "max_attempts", schema="jobs")
    op.drop_column("job_object", "attempts", schema="jobs")

"""create webhook table

Revision ID: 3b14d69ae793
Revises: 848d8d24a2bf
Create Date: 2025-12-16 03:27:03.002630
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "3b14d69ae793"
down_revision: Union[str, None] = "848d8d24a2bf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    op.create_table(
        "webhook_object",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("secret", sa.String(length=512), nullable=False),
        sa.Column("event_types", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenant.tenant_object.id"],
            name="fk_webhook_object_tenant_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_webhook_object"),
        schema="webhook",
    )

    # Indexes (tenant_id in particular is important)
    op.create_index(
        "ix_webhook_webhook_object_tenant_id",
        "webhook_object",
        ["tenant_id"],
        unique=False,
        schema="webhook",
    )


def downgrade() -> None:
    op.drop_index("ix_webhook_webhook_object_tenant_id", table_name="webhook_object", schema="webhook")
    op.drop_table("webhook_object", schema="webhook")

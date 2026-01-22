"""create tenant_object table

Revision ID: 9b3c4dbf4dd1
Revises: c3d0f6650144
Create Date: 2025-12-16 02:16:55.324213

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '9b3c4dbf4dd1'
down_revision: Union[str, None] = 'c3d0f6650144'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    op.create_table(
        "tenant_object",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("api_key_hash", sa.String(length=256), nullable=False),
        sa.Column("max_file_size_mb", sa.Integer(), nullable=False, server_default=sa.text("100")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id", name="pk_tenant_object"),
        schema="tenant",
    )

    op.create_index(
        "ix_tenant_tenant_object_name",
        "tenant_object",
        ["name"],
        unique=True,
        schema="tenant",
    )
    op.create_index(
        "ix_tenant_tenant_object_api_key_hash",
        "tenant_object",
        ["api_key_hash"],
        unique=True,
        schema="tenant",
    )


def downgrade() -> None:
    op.drop_index("ix_tenant_tenant_object_api_key_hash", table_name="tenant_object", schema="tenant")
    op.drop_index("ix_tenant_tenant_object_name", table_name="tenant_object", schema="tenant")
    op.drop_table("tenant_object", schema="tenant")

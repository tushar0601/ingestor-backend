"""create tenant schema

Revision ID: c3d0f6650144
Revises: 
Create Date: 2025-12-16 01:38:00.943907

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d0f6650144'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS tenant;")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS tenant;")

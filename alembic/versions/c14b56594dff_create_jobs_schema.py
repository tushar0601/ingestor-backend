"""create_jobs_schema

Revision ID: c14b56594dff
Revises: 0fb0f0373300
Create Date: 2025-12-16 03:22:25.818110

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c14b56594dff'
down_revision: Union[str, None] = '0fb0f0373300'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS jobs;")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS jobs;")

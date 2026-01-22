"""create_file_schema

Revision ID: f3cac7af148f
Revises: 9b3c4dbf4dd1
Create Date: 2025-12-16 03:04:14.143891

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f3cac7af148f'
down_revision: Union[str, None] = '9b3c4dbf4dd1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS file;")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS file;")

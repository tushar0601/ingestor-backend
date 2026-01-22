"""create webhooks schema

Revision ID: 848d8d24a2bf
Revises: c14b56594dff
Create Date: 2025-12-16 03:24:19.332036

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '848d8d24a2bf'
down_revision: Union[str, None] = 'c14b56594dff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS webhook;")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS webhook;")

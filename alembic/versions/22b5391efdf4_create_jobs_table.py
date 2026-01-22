"""create jobs table

Revision ID: 22b5391efdf4
Revises: 3b14d69ae793
Create Date: 2025-12-16 03:29:35.806497

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '22b5391efdf4'
down_revision: Union[str, None] = '3b14d69ae793'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

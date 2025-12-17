"""Merge heads

Revision ID: 7eb3147c36e4
Revises: 49d258bdc972, 5d43171a93f4
Create Date: 2025-12-12 00:16:44.261900

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7eb3147c36e4'
down_revision: Union[str, Sequence[str], None] = ('49d258bdc972', '5d43171a93f4')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

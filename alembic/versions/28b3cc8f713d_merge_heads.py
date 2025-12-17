"""merge heads

Revision ID: 28b3cc8f713d
Revises: a1b2c3d4e5f6, 92843d2c400f
Create Date: 2025-12-12 17:39:46.936438

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '28b3cc8f713d'
down_revision: Union[str, Sequence[str], None] = ('a1b2c3d4e5f6', '92843d2c400f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

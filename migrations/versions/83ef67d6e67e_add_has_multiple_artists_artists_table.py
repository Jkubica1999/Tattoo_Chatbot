"""add has_multiple_artists + artists table

Revision ID: 83ef67d6e67e
Revises: 41283c361e07
Create Date: 2025-10-20 03:24:21.736889

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '83ef67d6e67e'
down_revision: Union[str, Sequence[str], None] = '41283c361e07'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

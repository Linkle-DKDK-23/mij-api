"""Rename slug to profile_name and display_name to username

Revision ID: 6656ea5056dc
Revises: 4b6ee44d7feb
Create Date: 2025-09-29 17:14:37.174743

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6656ea5056dc'
down_revision: Union[str, Sequence[str], None] = '4b6ee44d7feb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename columns to preserve data
    op.alter_column('users', 'slug', new_column_name='profile_name')
    op.alter_column('profiles', 'display_name', new_column_name='username')


def downgrade() -> None:
    """Downgrade schema."""
    # Rename columns back to original names
    op.alter_column('users', 'profile_name', new_column_name='slug')
    op.alter_column('profiles', 'username', new_column_name='display_name')

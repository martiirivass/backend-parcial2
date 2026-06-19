"""add imagen_public_id to productos

Revision ID: 2a3b8957b5e3
Revises: 1a1b8957b5e2
Create Date: 2026-06-19 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a3b8957b5e3'
down_revision: Union[str, Sequence[str], None] = '1a1b8957b5e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'productos',
        sa.Column('imagen_public_id', sa.String(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('productos', 'imagen_public_id')

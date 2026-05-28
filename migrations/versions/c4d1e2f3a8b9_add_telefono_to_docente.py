"""add telefono to docente

Revision ID: c4d1e2f3a8b9
Revises: 6ef4efad3a6f
Create Date: 2026-05-28 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4d1e2f3a8b9'
down_revision: Union[str, Sequence[str], None] = '6ef4efad3a6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Agrega la columna telefono a la tabla docente."""
    op.add_column('docente', sa.Column('telefono', sa.String(length=20), nullable=True))


def downgrade() -> None:
    """Elimina la columna telefono de la tabla docente."""
    op.drop_column('docente', 'telefono')

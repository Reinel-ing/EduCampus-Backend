"""initial

Revision ID: 6bf1301c89d6
Revises: 6e47f93121af
Create Date: 2025-11-14 11:54:31.419384

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6bf1301c89d6'
down_revision: Union[str, Sequence[str], None] = '6e47f93121af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass
def downgrade() -> None:
    pass
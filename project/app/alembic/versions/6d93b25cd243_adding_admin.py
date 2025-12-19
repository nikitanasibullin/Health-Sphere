"""adding admin

Revision ID: 6d93b25cd243
Revises: bf440029d759
Create Date: 2025-12-19 02:41:51.200965

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import utils


# revision identifiers, used by Alembic.
revision: str = '6d93b25cd243'
down_revision: Union[str, Sequence[str], None] = 'bf440029d759'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    hashed_password = utils.hash("12345678")
    op.execute(f"""
        INSERT INTO users (email, password,user_type)
        VALUES ('admin@mail.ru','{hashed_password}','admin')
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass

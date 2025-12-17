"""adding admin

Revision ID: 0b4b33d3169c
Revises: a46f361280f9
Create Date: 2025-12-13 17:18:08.205013

"""
from typing import Sequence, Union
import utils
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0b4b33d3169c'
down_revision: Union[str, Sequence[str], None] = 'a46f361280f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    hashed_password = utils.hash("12345678")
    op.execute(f"""
        INSERT INTO users (email, password,user_type)
        VALUES ('admin@mail.ru','{hashed_password}','admin')
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass

"""users_table_changed

Revision ID: 020b1aab1d64
Revises: 3a1e3b1f3710
Create Date: 2025-02-03 15:09:01.223477

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '020b1aab1d64'
down_revision: Union[str, None] = '3a1e3b1f3710'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('hashed_password', sa.LargeBinary(), nullable=True))
    op.drop_column('users', 'password_hash')
    op.drop_column('users', 'solt')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('solt', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('password_hash', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('users', 'hashed_password')
    # ### end Alembic commands ###

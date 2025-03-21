"""promotion_images_added

Revision ID: 2b2e14af9c40
Revises: 6bc3f51ca47e
Create Date: 2025-01-22 22:01:55.396912

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b2e14af9c40'
down_revision: Union[str, None] = '6bc3f51ca47e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('promotion_images',
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('image_link', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('name')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('promotion_images')
    # ### end Alembic commands ###

"""number_of_sales_column_added_to_products

Revision ID: 84edf78775a7
Revises: 2b2e14af9c40
Create Date: 2025-01-23 20:58:33.478417

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '84edf78775a7'
down_revision: Union[str, None] = '2b2e14af9c40'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('products', sa.Column('number_of_sales', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('products', 'number_of_sales')
    # ### end Alembic commands ###

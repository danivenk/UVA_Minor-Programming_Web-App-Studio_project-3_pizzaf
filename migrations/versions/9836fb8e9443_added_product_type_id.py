"""added product_type_id

Revision ID: 9836fb8e9443
Revises: 403f329c4f15
Create Date: 2020-03-17 23:46:51.716889

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9836fb8e9443'
down_revision = '403f329c4f15'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Non-Pizza', sa.Column('product_type_id', sa.Integer(), nullable=True))
    op.add_column('Pizza', sa.Column('product_type_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Pizza', 'product_type_id')
    op.drop_column('Non-Pizza', 'product_type_id')
    # ### end Alembic commands ###
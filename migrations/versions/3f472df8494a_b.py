"""b

Revision ID: 3f472df8494a
Revises: 368b52f4414d
Create Date: 2020-03-17 14:49:41.465274

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f472df8494a'
down_revision = '368b52f4414d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Pizza', sa.Column('toppings', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Pizza', 'toppings')
    # ### end Alembic commands ###

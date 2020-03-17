"""size

Revision ID: d8535cc70224
Revises: ebc4afefde10
Create Date: 2020-03-17 12:18:18.620560

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd8535cc70224'
down_revision = 'ebc4afefde10'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Non-Pizza', sa.Column('size', sa.String(length=128), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Non-Pizza', 'size')
    # ### end Alembic commands ###

"""extras2

Revision ID: a73184dc9996
Revises: c1edf2b16969
Create Date: 2020-03-22 22:33:49.964801

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a73184dc9996'
down_revision = 'c1edf2b16969'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('extras')
    op.add_column('non-pizzas', sa.Column('extra_cheese', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('non-pizzas', 'extra_cheese')
    op.create_table('extras',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('extra', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.Column('cost', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='extras_pkey')
    )
    # ### end Alembic commands ###
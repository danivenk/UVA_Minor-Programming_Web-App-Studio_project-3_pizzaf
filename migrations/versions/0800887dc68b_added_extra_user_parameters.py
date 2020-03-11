"""added extra user parameters

Revision ID: 0800887dc68b
Revises: fa96e75fc55f
Create Date: 2020-03-10 12:13:46.800670

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0800887dc68b'
down_revision = 'fa96e75fc55f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('email', sa.String(length=128), nullable=False))
    op.add_column('users', sa.Column('first_name', sa.String(length=128), nullable=False))
    op.add_column('users', sa.Column('last_name', sa.String(length=128), nullable=False))
    op.add_column('users', sa.Column('password', sa.String(length=256), nullable=False))
    op.add_column('users', sa.Column('username', sa.String(length=128), nullable=False))
    op.drop_column('users', 'name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('name', sa.VARCHAR(length=128), autoincrement=False, nullable=True))
    op.drop_column('users', 'username')
    op.drop_column('users', 'password')
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'email')
    # ### end Alembic commands ###

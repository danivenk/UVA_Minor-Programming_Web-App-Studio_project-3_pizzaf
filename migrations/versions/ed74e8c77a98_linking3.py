"""linking3

Revision ID: ed74e8c77a98
Revises: 3c50b3d26f5a
Create Date: 2020-03-18 17:47:02.964329

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ed74e8c77a98'
down_revision = '3c50b3d26f5a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('products',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pizza_id', sa.Integer(), nullable=True),
    sa.Column('nonpizza_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['nonpizza_id'], ['non-pizzas.id'], ),
    sa.ForeignKeyConstraint(['pizza_id'], ['pizzas.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('order-items', sa.Column('product_id', sa.Integer(), nullable=True))
    op.drop_constraint('order-items_item_pizza_id_fkey', 'order-items', type_='foreignkey')
    op.drop_constraint('order-items_item_nonpizza_id_fkey', 'order-items', type_='foreignkey')
    op.create_foreign_key(None, 'order-items', 'products', ['product_id'], ['id'])
    op.drop_column('order-items', 'item_pizza_id')
    op.drop_column('order-items', 'item_nonpizza_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order-items', sa.Column('item_nonpizza_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('order-items', sa.Column('item_pizza_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'order-items', type_='foreignkey')
    op.create_foreign_key('order-items_item_nonpizza_id_fkey', 'order-items', 'non-pizzas', ['item_nonpizza_id'], ['id'])
    op.create_foreign_key('order-items_item_pizza_id_fkey', 'order-items', 'pizzas', ['item_pizza_id'], ['id'])
    op.drop_column('order-items', 'product_id')
    op.drop_table('products')
    # ### end Alembic commands ###
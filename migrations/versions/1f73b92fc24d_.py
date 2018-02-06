"""empty message

Revision ID: 1f73b92fc24d
Revises: 42adddd8b477
Create Date: 2018-02-05 23:17:40.269812

"""

# revision identifiers, used by Alembic.
revision = '1f73b92fc24d'
down_revision = '42adddd8b477'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('plan_todo', sa.Column('last_updated', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('plan_todo', 'last_updated')
    # ### end Alembic commands ###
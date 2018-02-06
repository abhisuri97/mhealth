"""empty message

Revision ID: e9f31a041383
Revises: 1f73b92fc24d
Create Date: 2018-02-06 00:10:47.000332

"""

# revision identifiers, used by Alembic.
revision = 'e9f31a041383'
down_revision = '1f73b92fc24d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('usage_stats',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('page', sa.String(length=1000), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.Column('length', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('usage_stats')
    # ### end Alembic commands ###

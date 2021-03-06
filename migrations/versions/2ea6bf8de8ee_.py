"""empty message

Revision ID: 2ea6bf8de8ee
Revises: 1ea5fa9c2c4f
Create Date: 2017-09-17 19:57:11.880552

"""

# revision identifiers, used by Alembic.
revision = '2ea6bf8de8ee'
down_revision = '1ea5fa9c2c4f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('exercises',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=1000), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('resources',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('aws_url', sa.String(length=10000), nullable=True),
    sa.Column('exercise_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['exercise_id'], ['exercises.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('resources')
    op.drop_table('exercises')
    ### end Alembic commands ###
